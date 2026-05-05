from src.app.repositories.user_repositories import UserRepository
from sqlmodel import Session

class UserService:
    
    def __init__(self, session: Session):
        self.user_repository = UserRepository(session=session)
    
    def get_email_by_user_id(self, user_id: str):
        return self.user_repository.get_email_by_user_id(user_id)
    
    def create_user(self, user_id: str, email: str, topics_of_interest: list[str]):
        return self.user_repository.create_user(user_id, email, topics_of_interest)