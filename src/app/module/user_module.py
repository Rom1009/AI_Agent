from src.app.core.base_module import BaseModule
from fastapi import APIRouter
from src.app.controller.user_controller import UserController
from src.db.db import engine
from sqlmodel import Session

class UserModule(BaseModule):

    prefix = "/users"
    tags = ["users"]

    def __init__(self, session: Session):
        super().__init__()
        self.user_controller = UserController(session = Session(bind=engine))

    def setup_router(self):
        self.router = APIRouter(prefix=self.prefix, tags=self.tags)
        self.router.post("/")(self.user_controller.create_user)
        self.router.get("/{user_id}/email")(self.user_controller.get_email_by_user_id)