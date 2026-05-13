import json 
import time 
from src.app.core.redis import r

def fake_model(text: str) -> str:
    time.sleep(5)
    return text.upper()

def process_job(job: dict):
    job_id = job["job_id"]
    text = job["text"]

    r.hset(f"job:{job_id}", "status", "PROCESSING")

    try:
        result = fake_model(text)

        r.hset(
            f"job:{job_id}",
            mapping = {
                "status": "DONE",
                "result": result,
                "error": ""
            },
        )

    except Exception as e:
        r.hset(
            f"job:{job_id}",
            mapping = {
                "status": "FAILED",
                "result": "",
                "error": str(e)
            }
        )


def main():
    print("Worker started. Waiting for jobs...")
    while True:
        _, raw_job = r.blpop("ai_job")
        job = json.loads(raw_job)

        process_job(job)

if __name__ == "__main__":
    main()