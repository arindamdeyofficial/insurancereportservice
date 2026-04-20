from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.article import Article
from app.models.incident import Incident
from app.models.sentiment import Sentiment
from app.models.rival_ad import RivalAd
from app.services.mcp_client import analyze_article
from app.services.scraper import fetch_articles, fetch_from_sources
from app.services import clickhouse_client as ch
from app.services.cache import cache_delete_pattern


def process_article(article_id: int):
    db: Session = SessionLocal()
    try:
        article = db.get(Article, article_id)
        if not article:
            return
        results = analyze_article(article.raw_text)

        inc = results["incident"]
        if inc.get("incident"):
            db.add(Incident(
                article_id=article.id,
                summary=inc.get("summary", ""),
                severity=inc.get("severity", "none"),
            ))
            ch.insert_incident(article.id, article.source, inc.get("severity", "none"))

        sent = results["sentiment"]
        score = float(sent.get("score", 0.0))
        label = sent.get("label", "neutral")
        db.add(Sentiment(article_id=article.id, score=score, label=label, reasoning=sent.get("reasoning", "")))
        ch.insert_sentiment(article.id, article.source, score, label)

        rival = results["rival_ad"]
        if rival.get("is_rival_ad"):
            competitor = rival.get("competitor", "")
            db.add(RivalAd(article_id=article.id, competitor_name=competitor, ad_summary=rival.get("ad_summary", "")))
            ch.insert_rival_ad(article.id, article.source, competitor)

        db.commit()

        # invalidate Redis caches so next read is fresh
        cache_delete_pattern("incidents:*")
        cache_delete_pattern("sentiments:*")
        cache_delete_pattern("rival_ads:*")
        cache_delete_pattern("analytics:*")
    finally:
        db.close()


def _enqueue_articles(articles: list[dict]):
    from app.services.kafka_producer import publish_article, flush

    db: Session = SessionLocal()
    source_counts: dict[str, int] = {}
    try:
        for art in articles:
            existing = db.query(Article).filter_by(url=art["url"]).first()
            if existing:
                continue
            db_article = Article(**art)
            db.add(db_article)
            db.flush()
            publish_article(db_article.id, {"source": art["source"], "title": art["title"]})
            source_counts[art["source"]] = source_counts.get(art["source"], 0) + 1
        db.commit()
        flush()

        for source, count in source_counts.items():
            ch.insert_scrape_metric(source, count)
    finally:
        db.close()


def ingest_news():
    _enqueue_articles(fetch_articles())


def ingest_news_sources(sources: list[dict]):
    _enqueue_articles(fetch_from_sources(sources))
