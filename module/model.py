from pydantic import BaseModel, Field
from typing import Literal

class DigestRequest(BaseModel):
    user_id: str | None = Field(default = "default_user")
    run_date: str | None = Field(default = None, description = "YYYY-MM-DD")
    topics: list[str] = Field(default_factory = list)
    max_articles_per_topic: int = Field(default = 3, ge = 1, le = 10)
    output_language: Literal["vi", "en"] = "vi"
    digest_style: Literal["brief", "executive", "bullet"] = "brief"
    include_domains: list[str] = Field(default_factory = list)
    exclude_domains: list[str] = Field(default_factory = list)
    dry_run: bool = False


class DigestResponse(BaseModel):
    subjects: str 
    markdown: str
    warnings: list[str] = Field(default_factory = list)
    source_count: int = 0