from datetime import datetime
from pydantic import BaseModel
from app.schemas.article import ArticleOut


class SentimentOut(BaseModel):
    id: int
    article_id: int
    score: float
    label: str
    reasoning: str
    created_at: datetime
    article: ArticleOut

    model_config = {"from_attributes": True}
