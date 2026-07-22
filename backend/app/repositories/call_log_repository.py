"""In-memory call/webhook event log."""

from threading import Lock
from typing import Any, Dict, List

from backend.app.models.call import CallLogEntry


class CallLogRepository:
    def __init__(self) -> None:
        self._lock = Lock()
        self._logs: List[CallLogEntry] = []

    def append(self, event: str, timestamp: str, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._logs.append(CallLogEntry(event=event, timestamp=timestamp, payload=payload))

    def list_all(self) -> List[CallLogEntry]:
        with self._lock:
            return list(self._logs)


call_log_repository = CallLogRepository()
