from src.app.core.base_module import BaseModule
from fastapi import APIRouter
from src.app.controller.user_controller import UserController

class UserModule(BaseModule):

    prefix = "/users"
    tags = ["users"]

    def __init__(self):
        super().__init__()
        self.user_controller = UserController()

    def setup_router(self):
        self.router = APIRouter()
        self.router.post("/")(self.user_controller.create_user)