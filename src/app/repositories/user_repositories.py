from src.app.schema.model import User
from sqlmodel import Session, select

class UserRepository:

    def __init__(self, session: Session):
        self.session = session
    
    def get_email_by_user_id(self, user_id: str):
        statement = select(User).where(User.user_id == user_id)
        return self.session.exec(statement).first()
    
    def create_user(self, user_id: str, email: str, topics_of_interest: list[str]):
        new_user = User(user_id = user_id, email=email, topics_of_interest=topics_of_interest)
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)

