from src.app.repositories.user_repositories import UserRepository
from sqlmodel import Session
from src.utils.logger import setup_logger
from src.app.exceptions.exceptions import UserAlreadyExist

logger = setup_logger("User Service")

class UserService:
    
    def __init__(self, session: Session):
        self.user_repository = UserRepository(session=session)
    
    def create_user(self, user_data: dict):
        logger.info(f"Creating user with email: {user_data.get('email')}")

        if self.user_repository.get_user_by_email(user_data.get("email")):
            logger.warning(f"User with email {user_data.get('email')} already exists")
            raise UserAlreadyExist(
                message=f"User with email {user_data.get('email')} already exists",
                details={"email": user_data.get("email")}
            )

        return self.user_repository.create_user(user_data)