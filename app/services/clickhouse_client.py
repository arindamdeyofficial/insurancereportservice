import os
import clickhouse_connect

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "host.docker.internal")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")

_client = None

DDL = [
    """
    CREATE TABLE IF NOT EXISTS sentiment_analytics (
        event_time  DateTime DEFAULT now(),
        article_id  UInt32,
        source      String,
        language    String DEFAULT 'english',
        score       Float32,
        label       String,
        date        Date DEFAULT toDate(event_time)
    ) ENGINE = MergeTree()
    PARTITION BY toYYYYMM(event_time)
    ORDER BY (date, source)
    """,
    """
    CREATE TABLE IF NOT EXISTS incident_analytics (
        event_time  DateTime DEFAULT now(),
        article_id  UInt32,
        source      String,
        severity    String,
        date        Date DEFAULT toDate(event_time)
    ) ENGINE = MergeTree()
    PARTITION BY toYYYYMM(event_time)
    ORDER BY (date, severity)
    """,
    """
    CREATE TABLE IF NOT EXISTS rival_ad_analytics (
        event_time   DateTime DEFAULT now(),
        article_id   UInt32,
        competitor   String,
        source       String,
        date         Date DEFAULT toDate(event_time)
    ) ENGINE = MergeTree()
    PARTITION BY toYYYYMM(event_time)
    ORDER BY (date, competitor)
    """,
    """
    CREATE TABLE IF NOT EXISTS scrape_metrics (
        event_time   DateTime DEFAULT now(),
        source       String,
        articles_fetched UInt32,
        date         Date DEFAULT toDate(event_time)
    ) ENGINE = MergeTree()
    ORDER BY (date, source)
    """,
]


def get_client():
    global _client
    if _client is None:
        _client = clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            username=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
        )
    return _client


def init_tables():
    try:
        c = get_client()
        for ddl in DDL:
            c.command(ddl)
        print("[ClickHouse] Tables ready.")
    except Exception as e:
        print(f"[ClickHouse] Init failed: {e}")


def insert_sentiment(article_id: int, source: str, score: float, label: str, language: str = "english"):
    try:
        get_client().insert("sentiment_analytics",
            [[article_id, source, language, score, label]],
            column_names=["article_id", "source", "language", "score", "label"])
    except Exception as e:
        print(f"[ClickHouse] insert_sentiment error: {e}")


def insert_incident(article_id: int, source: str, severity: str):
    try:
        get_client().insert("incident_analytics",
            [[article_id, source, severity]],
            column_names=["article_id", "source", "severity"])
    except Exception as e:
        print(f"[ClickHouse] insert_incident error: {e}")


def insert_rival_ad(article_id: int, source: str, competitor: str):
    try:
        get_client().insert("rival_ad_analytics",
            [[article_id, source, competitor]],
            column_names=["article_id", "source", "competitor"])
    except Exception as e:
        print(f"[ClickHouse] insert_rival_ad error: {e}")


def insert_scrape_metric(source: str, count: int):
    try:
        get_client().insert("scrape_metrics",
            [[source, count]],
            column_names=["source", "articles_fetched"])
    except Exception as e:
        print(f"[ClickHouse] insert_scrape_metric error: {e}")


# ── Analytics queries ─────────────────────────────────────────────────────────

def sentiment_trend(days: int = 30) -> list[dict]:
    try:
        r = get_client().query(f"""
            SELECT date, label, count() AS cnt
            FROM sentiment_analytics
            WHERE date >= today() - {days}
            GROUP BY date, label
            ORDER BY date
        """)
        return [{"date": str(row[0]), "label": row[1], "count": row[2]} for row in r.result_rows]
    except Exception as e:
        print(f"[ClickHouse] sentiment_trend error: {e}")
        return []


def incident_trend(days: int = 30) -> list[dict]:
    try:
        r = get_client().query(f"""
            SELECT date, severity, count() AS cnt
            FROM incident_analytics
            WHERE date >= today() - {days}
            GROUP BY date, severity
            ORDER BY date
        """)
        return [{"date": str(row[0]), "severity": row[1], "count": row[2]} for row in r.result_rows]
    except Exception as e:
        print(f"[ClickHouse] incident_trend error: {e}")
        return []


def rival_leaderboard(days: int = 30) -> list[dict]:
    try:
        r = get_client().query(f"""
            SELECT competitor, count() AS cnt
            FROM rival_ad_analytics
            WHERE date >= today() - {days}
            GROUP BY competitor
            ORDER BY cnt DESC
            LIMIT 10
        """)
        return [{"competitor": row[0], "count": row[1]} for row in r.result_rows]
    except Exception as e:
        print(f"[ClickHouse] rival_leaderboard error: {e}")
        return []


def source_activity(days: int = 30) -> list[dict]:
    try:
        r = get_client().query(f"""
            SELECT date, source, sum(articles_fetched) AS articles
            FROM scrape_metrics
            WHERE date >= today() - {days}
            GROUP BY date, source
            ORDER BY date, source
        """)
        return [{"date": str(row[0]), "source": row[1], "articles": row[2]} for row in r.result_rows]
    except Exception as e:
        print(f"[ClickHouse] source_activity error: {e}")
        return []
