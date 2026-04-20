import feedparser
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone

NEWS_SOURCES = [
    {"name": "Times of India",   "rss": "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms", "scrape": False},
    {"name": "The Hindu",        "rss": "https://www.thehindu.com/business/Industry/feeder/default.rss", "scrape": False},
    {"name": "Economic Times",   "rss": "https://economictimes.indiatimes.com/industry/banking/insurance/rssfeeds/13358259.cms", "scrape": False},
    {"name": "Moneycontrol",     "rss": "https://www.moneycontrol.com/rss/business.xml", "scrape": False},
    {"name": "Telegraph India",  "rss": "https://www.telegraphindia.com/rss/business.xml", "scrape": True},
]

KEYWORDS = [
    "guardian insurance", "insurance claim", "insurance fraud", "insurance complaint",
    "insurance policy", "insurer", "LIC", "HDFC Ergo", "ICICI Lombard",
    "New India Assurance", "Bajaj Allianz", "Star Health", "SBI Life",
    "Max Life", "Tata AIG", "Reliance General",
]


def _is_relevant(text: str) -> bool:
    lower = text.lower()
    return any(kw.lower() in lower for kw in KEYWORDS)


def _scrape_article_text(url: str) -> str:
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            resp = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()
        return " ".join(p.get_text(strip=True) for p in soup.find_all("p"))[:8000]
    except Exception:
        return ""


def _parse_feed(source_name: str, rss_url: str, do_scrape: bool) -> list[dict]:
    results = []
    feed = feedparser.parse(rss_url)
    for entry in feed.entries[:20]:
        title = entry.get("title", "")
        url = entry.get("link", "")
        summary = entry.get("summary", "")
        if not _is_relevant(f"{title} {summary}"):
            continue
        text = summary
        if do_scrape and url:
            scraped = _scrape_article_text(url)
            if scraped:
                text = scraped
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        results.append({
            "source": source_name,
            "url": url,
            "title": title,
            "raw_text": text or summary,
            "published_at": published,
        })
    return results


def fetch_articles() -> list[dict]:
    results = []
    for s in NEWS_SOURCES:
        results.extend(_parse_feed(s["name"], s["rss"], s["scrape"]))
    return results


def fetch_from_sources(sources: list[dict]) -> list[dict]:
    """sources: list of {name, rss, url, scrape}"""
    results = []
    for s in sources:
        rss = s.get("rss") or ""
        if rss:
            results.extend(_parse_feed(s["name"], rss, s.get("scrape", False)))
    return results
