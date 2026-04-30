from sqlmodel import Session, create_engine, SQLModel, select
from src.utils.config import settings
from src.app.schema.model import Article, User, Joblog

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)

def is_already_sent(url: str) -> bool:
    with Session(engine) as session:
        statement =  select(Article).where(Article.url == url)
        result = session.exec(statement).first()

        return result is not None

def add_to_history(article: Article):
    with Session(engine) as session:
        session.add(article)
        session.commit()