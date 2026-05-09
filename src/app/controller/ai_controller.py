from fastapi.responses import StreamingResponse
from src.app.services.ai_services import AIService

class AIController:
    
    def __init__(self):
        self.ai_service = AIService()

    async def generate_response(self, prompt: str):
        gen = self.ai_service.generate_chat_stream(prompt)
        return StreamingResponse(gen, media_type="text/event-stream")
    