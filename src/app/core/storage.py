import json 
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


JOB_HISTORY_FILE = Path("job_history.jsonl")
DLQ_FILE = Path("dlq.jsonl")

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    with path.open("a", encoding = "utf-8") as f:
        f.write(json.dumps(record, ensure_ascii = False) + "\n")

def log_event(task_id: str, event: str, payload: dict[str, Any] | None = None) -> None:
    record = {
        "timestamp": utc_now(), 
        "task_id": task_id,
        "event": event,
        "payload": payload or {}
    }
    append_jsonl(JOB_HISTORY_FILE, record)

def send_to_dlq(task_id: str, reason: str, payload: dict[str, Any] | None = None) -> None:
    record = {
        "timestamp": utc_now(),
        "task_id": task_id,
        "reason": reason,
        "payload": payload or {}
    }
    append_jsonl(DLQ_FILE, record)

def read_jsonl(path: Path, limit: int = 50) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    
    lines = path.read_text(encoding = "utf-8").splitlines()
    last_lines = lines[-limit:]

    records = []
    for line in last_lines:
        if line.strip():
            records.append(json.loads(line))

    return records

def read_history(limit: int = 50) -> list[dict[str, Any]]:
    return read_jsonl(JOB_HISTORY_FILE, limit)

def read_dlq(limit: int = 50) -> list[dict[str, Any]]:
    return read_jsonl(DLQ_FILE, limit)