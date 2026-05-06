from src.app.services.user_service import UserService
from src.app.schema.model import UserRequest, UserResponse
from sqlmodel import Session
from src.db.db import get_session
from fastapi import Depends

class UserController:
      
    def create_user(self, user_request: UserRequest, session: Session = Depends(get_session)) -> UserResponse:
        user_data = user_request.model_dump()
        user_service = UserService(session)

        new_user = user_service.create_user(user_data)
        return UserResponse.model_validate(new_user)
