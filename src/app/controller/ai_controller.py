import json

from fastapi.responses import StreamingResponse
from src.app.services.ai_services import AIService
from src.app.schema.model import JobRequest
from uuid import uuid4
from src.app.core.redis import r

from src.app.core.tasks import process_text_job
from celery.result import AsyncResult
from src.app.core.celery_app import celery_app

class AIController:
    
    def __init__(self):
        self.ai_service = AIService()

    async def generate_response(self, prompt: str):
        gen = self.ai_service.generate_response(prompt)
        return StreamingResponse(gen, media_type="text/event-stream")
    
    def health_check(self):
        return {"status": "ok", "message": "AI Controller is healthy"}
    
    # def submit_job(self, request: JobRequest):
    #     job_id = str(uuid4())
    #     job = {
    #         "job_id": job_id,
    #         "text": request.text
    #     }

    #     r.hset(
    #         f"job:{job_id}",
    #         mapping = {
    #             "status": "QUEUED",
    #             "result": "",
    #             "error": ""
    #         }
    #     )

    #     r.lpush("ai_job", json.dumps(job))

    #     return {
    #         "job_id": job_id,
    #         "status": "QUEUED"
    #     }
    
    # def get_result(self, job_id: str):
    #     job = r.hgetall(f"job:{job_id}")

    #     if not job: 
    #         return {
    #             "job_id": job_id,
    #             "status": "NOT_FOUND",
    #             "result": "",
    #             "error": "Job not found"
    #         }

    #     return {
    #         "job_id": job_id,
    #         "status": job.get("status", "UNKNOWN"),
    #         "result": job.get("result", ""),
    #         "error": job.get("error", "")
    #     }

    # def get_queue_size(self):
        size = r.llen("ai_job")
        return {
            "queue": "ai_job",
            "size": size
        }

    def submit_job(self, request: JobRequest):
        task = process_text_job.delay(request.text)

        return {
            "task_id": task.id,
            "status": "SUBMITTED"
        }

    def get_result(self, task_id: str):
        task_result = AsyncResult(task_id, app=celery_app)

        response = {
            "task_id": task_id,
            "status": task_result.status,
            "result": None,
            "error": None
        }

        if task_result.successful():
            response["result"] = task_result.result
        elif task_result.failed():
            response["error"] = str(task_result.result)

        return response