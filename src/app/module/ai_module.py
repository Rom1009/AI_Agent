from src.app.controller.ai_controller import AIController
from fastapi import APIRouter

class AIModule:

    prefix = "/ai"
    tags = ["ai"]

    def __init__(self):
        super().__init__()
        self.ai_controller = AIController()

    def setup_router(self):
        self.router = APIRouter()
        self.router.get("/generate")(self.ai_controller.generate_response)
