import json
import threading
import os
from confluent_kafka import Consumer, KafkaError

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "host.docker.internal:9092")
TOPIC_RAW = "insurance.raw_articles"

_thread: threading.Thread | None = None
_running = False


def _consume_loop():
    consumer = Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": "insurance-analyzer",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })
    consumer.subscribe([TOPIC_RAW])
    print(f"[Kafka Consumer] Subscribed to {TOPIC_RAW}")

    while _running:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                print(f"[Kafka Consumer] Error: {msg.error()}")
            continue
        try:
            data = json.loads(msg.value())
            article_id = data.get("article_id")
            if article_id:
                from app.services.worker import process_article
                process_article(article_id)
        except Exception as e:
            print(f"[Kafka Consumer] Processing error: {e}")

    consumer.close()
    print("[Kafka Consumer] Stopped.")


def start_consumer():
    global _thread, _running
    _running = True
    _thread = threading.Thread(target=_consume_loop, daemon=True, name="kafka-consumer")
    _thread.start()
    print("[Kafka Consumer] Started.")


def stop_consumer():
    global _running
    _running = False


if __name__ == "__main__":
    import signal, sys
    _running = True
    print("[Kafka Worker] Starting standalone consumer...")

    consumer = __import__("confluent_kafka", fromlist=["Consumer"]).Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": "insurance-analyzer",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })
    consumer.subscribe([TOPIC_RAW])

    def _shutdown(sig, frame):
        print("[Kafka Worker] Shutting down...")
        consumer.close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"[Kafka Worker] Error: {msg.error()}")
            continue
        try:
            data = __import__("json").loads(msg.value())
            article_id = data.get("article_id")
            if article_id:
                from app.services.worker import process_article
                process_article(article_id)
                print(f"[Kafka Worker] Processed article {article_id}")
        except Exception as e:
            print(f"[Kafka Worker] Error processing message: {e}")
