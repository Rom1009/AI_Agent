import random
import time
from src.app.core.celery_app import celery_app
from src.app.core.errors import PermanentAIError, TransientAIError
from src.app.core.storage import log_event,send_to_dlq
from celery.exceptions import SoftTimeLimitExceeded


# def fake_model(text: str) -> str:
#     time .sleep(10)
#     if text.lower().strip() == "fail":
#         raise ValueError("Fake model failed because input was 'fail'")
#     return text.upper()

# @celery_app.task(
#     bind=True, 
#     name = "tasks.process_text_job",
#     max_retries = 3,
#     default_retry_delay = 3
# )
# def process_text_job(self, text: str) -> str:
#     try:
#         result = fake_model(text)

#         return {
#             "input": text,
#             "result": result, 
#             "model": "fake_model_v1"
#         }
#     except Exception as e:
#         raise self.retry(exc=e)

def fake_model(text: str) -> str:
    cleaned = text.strip().lower()

    if not cleaned:
        raise PermanentAIError("Input text is empty")

    if cleaned == "bad":
        raise PermanentAIError("Invalid input: 'bad' is not allowed")

    if cleaned == "timeout":
        time.sleep(30)
        return "This should timeout"

    if cleaned == "unstable":
        # Gia lap loi tam thoi luc co luc khong
        if random.random() < 0.7:
            raise TransientAIError("Temporary upstream AI service error")

    time.sleep(5)
    return text.upper()

@celery_app.task(
    bind = True, 
    name = "tasks.reliable_process_text_task",
    max_retries = 3,
    default_retry_delay = 3
)
def reliable_process_text_task(self, text: str) -> str:
    task_id = self.request.id

    log_event(
        task_id = task_id,
        event = "TASK_STARTED",
        payload = {
            "text": text,
            "retry_count": self.request.retries 
        }
    )

    try: 
        result = fake_model(text)

        response = {
            "input": text,
            "result": result,
            "model": "fake-uppercase-model-v2-reliable",
            "retry_count": self.request.retries,
        }

        log_event(
            task_id=task_id,
            event="TASK_SUCCEEDED",
            payload=response,
        )

        return response

    except PermanentAIError as exc:
        error_payload = {
            "error_type": "PERMANENT",
            "message": str(exc),
            "input": text,
            "retry_count": self.request.retries,
        }

        log_event(
            task_id=task_id,
            event="TASK_FAILED_PERMANENT",
            payload=error_payload,
        )

        send_to_dlq(
            task_id=task_id,
            reason="PERMANENT_ERROR",
            payload=error_payload,
        )

        raise exc

    except TransientAIError as exc:
        error_payload = {
            "error_type": "TRANSIENT",
            "message": str(exc),
            "input": text,
            "retry_count": self.request.retries,
        }

        log_event(
            task_id=task_id,
            event="TASK_TRANSIENT_ERROR",
            payload=error_payload,
        )

        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            send_to_dlq(
                task_id=task_id,
                reason="MAX_RETRIES_EXCEEDED",
                payload=error_payload,
            )
            raise exc

    except SoftTimeLimitExceeded as exc:
        error_payload = {
            "error_type": "TIMEOUT",
            "message": "Task exceeded soft time limit",
            "input": text,
            "retry_count": self.request.retries,
        }

        log_event(
            task_id=task_id,
            event="TASK_TIMEOUT",
            payload=error_payload,
        )

        send_to_dlq(
            task_id=task_id,
            reason="TIMEOUT",
            payload=error_payload,
        )

        raise exc

    except Exception as exc:
        error_payload = {
            "error_type": "UNKNOWN",
            "message": str(exc),
            "input": text,
            "retry_count": self.request.retries,
        }

        log_event(
            task_id=task_id,
            event="TASK_FAILED_UNKNOWN",
            payload=error_payload,
        )

        send_to_dlq(
            task_id=task_id,
            reason="UNKNOWN_ERROR",
            payload=error_payload,
        )

        raise exc