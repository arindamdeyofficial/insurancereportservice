from datetime import datetime
from pydantic import BaseModel


class WebsiteCreate(BaseModel):
    name: str
    url: str
    rss_url: str | None = None
    language: str = "english"
    is_active: bool = True


class WebsiteOut(BaseModel):
    id: int
    name: str
    url: str
    rss_url: str | None
    language: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
