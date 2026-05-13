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
        self.router.get("/health")(self.ai_controller.health_check)
        self.router.post("/submit")(self.ai_controller.submit_job)
        self.router.get("/result/{job_id}")(self.ai_controller.get_result)
        self.router.get("/queue_size")(self.ai_controller.get_queue_size)
