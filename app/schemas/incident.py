from datetime import datetime
from pydantic import BaseModel
from app.schemas.article import ArticleOut


class IncidentOut(BaseModel):
    id: int
    article_id: int
    summary: str
    severity: str
    created_at: datetime
    article: ArticleOut

    model_config = {"from_attributes": True}
