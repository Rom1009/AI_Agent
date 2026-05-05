from sqlmodel import create_engine, SQLModel
from src.utils.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)