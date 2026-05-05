from src.app.services.user_service import UserService
from sqlmodel import Session

class UserController:
    
    def __init__(self, session: Session):
        self.user_service = UserService(session=session)
    
    def get_email_by_user_id(self, user_id: str):
        return self.user_service.get_email_by_user_id(user_id)
    
    def create_user(self, user_id: str, email: str, topics_of_interest: list[str]):
        return self.user_service.create_user(user_id, email, topics_of_interest)