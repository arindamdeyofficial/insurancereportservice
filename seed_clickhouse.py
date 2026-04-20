"""Seed ClickHouse with historical analytics matching existing DB data.
Run after rebuild: docker exec insuranceai-api-1 python seed_clickhouse.py
"""
import os, sys
sys.path.insert(0, "/app")

from datetime import datetime, timedelta, timezone
import clickhouse_connect

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "host.docker.internal")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")

c = clickhouse_connect.get_client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD)

# ensure tables
for ddl in [
    """CREATE TABLE IF NOT EXISTS sentiment_analytics (
        event_time DateTime DEFAULT now(), article_id UInt32, source String,
        language String DEFAULT 'english', score Float32, label String,
        date Date DEFAULT toDate(event_time)
    ) ENGINE=MergeTree() PARTITION BY toYYYYMM(event_time) ORDER BY (date,source)""",
    """CREATE TABLE IF NOT EXISTS incident_analytics (
        event_time DateTime DEFAULT now(), article_id UInt32, source String,
        severity String, date Date DEFAULT toDate(event_time)
    ) ENGINE=MergeTree() PARTITION BY toYYYYMM(event_time) ORDER BY (date,severity)""",
    """CREATE TABLE IF NOT EXISTS rival_ad_analytics (
        event_time DateTime DEFAULT now(), article_id UInt32, competitor String,
        source String, date Date DEFAULT toDate(event_time)
    ) ENGINE=MergeTree() PARTITION BY toYYYYMM(event_time) ORDER BY (date,competitor)""",
    """CREATE TABLE IF NOT EXISTS scrape_metrics (
        event_time DateTime DEFAULT now(), source String,
        articles_fetched UInt32, date Date DEFAULT toDate(event_time)
    ) ENGINE=MergeTree() ORDER BY (date,source)""",
]:
    c.command(ddl)

now = datetime.now(timezone.utc)

# ── Sentiment analytics (30 days of history) ─────────────────────────────────
sources = ["Times of India","The Hindu","Economic Times","Hindustan Times","Mint",
           "Telegraph India","Dainik Bhaskar","Amar Ujala","Navbharat Times","Business Standard"]
labels_cycle = ["positive","negative","neutral","negative","positive","neutral","negative","positive","neutral","negative"]
scores_cycle  = [0.75, -0.80, 0.05, -0.65, 0.60, 0.10, -0.72, 0.55, 0.02, -0.50]

sent_rows = []
for day in range(30, 0, -1):
    dt = now - timedelta(days=day)
    for i, src in enumerate(sources):
        for _ in range(2):
            sent_rows.append([dt, 1000+day*10+i, src, "english",
                              scores_cycle[i], labels_cycle[i]])

c.insert("sentiment_analytics",
    sent_rows,
    column_names=["event_time","article_id","source","language","score","label"])

# ── Incident analytics ───────────────────────────────────────────────────────
inc_rows = []
sev_cycle = ["high","medium","low","high","medium"]
for day in range(30, 0, -1):
    dt = now - timedelta(days=day)
    count = 3 if day % 5 == 0 else (2 if day % 3 == 0 else 1)
    for i in range(count):
        inc_rows.append([dt, 2000+day*5+i, sources[i % len(sources)], sev_cycle[i % 5]])

c.insert("incident_analytics",
    inc_rows,
    column_names=["event_time","article_id","source","severity"])

# ── Rival ad analytics ───────────────────────────────────────────────────────
rivals = ["LIC","HDFC Ergo","ICICI Lombard","Bajaj Allianz","Star Health","SBI Life","Tata AIG"]
rival_rows = []
for day in range(30, 0, -1):
    dt = now - timedelta(days=day)
    for i in range(day % 4 + 1):
        rival_rows.append([dt, 3000+day*4+i, rivals[i % len(rivals)], sources[i % len(sources)]])

c.insert("rival_ad_analytics",
    rival_rows,
    column_names=["event_time","article_id","competitor","source"])

# ── Scrape metrics ───────────────────────────────────────────────────────────
scrape_rows = []
for day in range(30, 0, -1):
    dt = now - timedelta(days=day)
    for src in sources:
        scrape_rows.append([dt, src, 5 + (day % 8)])

c.insert("scrape_metrics",
    scrape_rows,
    column_names=["event_time","source","articles_fetched"])

print(f"✓ Seeded ClickHouse: {len(sent_rows)} sentiment, {len(inc_rows)} incident, {len(rival_rows)} rival_ad, {len(scrape_rows)} scrape_metric rows.")
