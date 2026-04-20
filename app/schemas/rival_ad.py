from datetime import datetime
from pydantic import BaseModel
from app.schemas.article import ArticleOut


class RivalAdOut(BaseModel):
    id: int
    article_id: int
    competitor_name: str
    ad_summary: str
    created_at: datetime
    article: ArticleOut

    model_config = {"from_attributes": True}
