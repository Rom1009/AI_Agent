from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON
from enum import Enum
from uuid import uuid4

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

class JobStatus(str, Enum):
    success = "success"
    failure = "failure"

class Article(SQLModel, table = True):
    url: str = Field(primary_key=True)
    title: str
    source: Optional[str] = None
    sent_at: datetime = Field(default_factory = datetime.utcnow)

class User(SQLModel, table = True):
    user_id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    email: str
    topics_of_interest: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_active: bool = True

class Joblog(SQLModel, table = True):
    job_id: str = Field(primary_key=True)
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: JobStatus = Field(default=JobStatus.success)
    error_message: str | None = None

class UserResponse(SQLModel):
    user_id: str
    email: str
    topics_of_interest: list[str] = Field(default_factory=list)

class UserRequest(SQLModel):
    email: str
    topics_of_interest: list[str] = Field(default_factory=list)