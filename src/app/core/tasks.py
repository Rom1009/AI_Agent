import time
from src.app.core.celery_app import celery_app


def fake_model(text: str) -> str:
    time .sleep(10)
    if text.lower().strip() == "fail":
        raise ValueError("Fake model failed because input was 'fail'")
    return text.upper()

@celery_app.task(
    bind=True, 
    name = "tasks.process_text_job",
    max_retries = 3,
    default_retry_delay = 3
)
def process_text_job(self, text: str) -> str:
    try:
        result = fake_model(text)

        return {
            "input": text,
            "result": result, 
            "model": "fake_model_v1"
        }
    except Exception as e:
        raise self.retry(exc=e)