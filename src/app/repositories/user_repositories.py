from src.app.schema.model import User
from sqlmodel import Session, select
from src.utils.logger import setup_logger

logger = setup_logger("User Repository")

class UserRepository:

    def __init__(self, session: Session):
        self.session = session
    
    def get_user_by_email(self, email: str):
        statement = select(User).where(User.email == email)
        logger.info(f"Fetching user with email: {email}")
        return self.session.exec(statement).first()
    
    def create_user(self, user_data):
        logger.info(f"Creating user with email: {user_data.get('email')}")
        new_user = User(**user_data)
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        logger.info(f"User created: {new_user.user_id}")
        return new_user


