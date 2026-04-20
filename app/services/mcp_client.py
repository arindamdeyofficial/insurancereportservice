import httpx
import os

MCP_BASE_URL = os.getenv("MCP_URL", "http://localhost:8001")


def _post(path: str, article_text: str) -> dict:
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(
            f"{MCP_BASE_URL}{path}",
            json={"article_text": article_text},
        )
        resp.raise_for_status()
        return resp.json()


def analyze_article(article_text: str) -> dict:
    incident = _post("/extract-incidents", article_text)
    sentiment = _post("/analyze-sentiment", article_text)
    rival = _post("/detect-rival-ads", article_text)
    return {"incident": incident, "sentiment": sentiment, "rival_ad": rival}
