from src.app.repositories.user_repositories import UserRepository
from sqlmodel import Session

class UserService:
    
    def __init__(self, session: Session):
        self.user_repository = UserRepository(session=session)
    
    def create_user(self, user_data: dict):
        return self.user_repository.create_user(user_data)