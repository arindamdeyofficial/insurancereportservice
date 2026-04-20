import json
import os
from confluent_kafka import Producer

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "host.docker.internal:9092")
TOPIC_RAW = "insurance.raw_articles"

_producer: Producer | None = None


def get_producer() -> Producer:
    global _producer
    if _producer is None:
        _producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP, "client.id": "insurancereportservice"})
    return _producer


def publish_article(article_id: int, article_data: dict):
    try:
        p = get_producer()
        payload = json.dumps({"article_id": article_id, **article_data}, default=str)
        p.produce(TOPIC_RAW, key=str(article_id), value=payload)
        p.poll(0)
    except Exception as e:
        print(f"[Kafka] Failed to publish article {article_id}: {e}")


def flush():
    try:
        get_producer().flush(timeout=5)
    except Exception:
        pass
