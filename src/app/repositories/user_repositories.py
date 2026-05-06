from src.app.schema.model import User
from sqlmodel import Session, select

class UserRepository:

    def __init__(self, session: Session):
        self.session = session
    
    def get_user_by_email(self, email: str):
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
    
    def create_user(self, user_data):
        new_user = User(**user_data)
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user


