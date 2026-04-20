from datetime import datetime
from pydantic import BaseModel


class ArticleOut(BaseModel):
    id: int
    source: str
    url: str
    title: str
    published_at: datetime | None
    scraped_at: datetime

    model_config = {"from_attributes": True}
