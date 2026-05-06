from sqlmodel import create_engine, SQLModel
from src.utils.config import settings
from typing import Generator
from sqlmodel import Session

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

def init_db(): 
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session