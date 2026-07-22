"""In-memory registry of calls that are currently ringing/in-progress."""

from threading import Lock
from typing import Dict, List, Optional

from backend.app.models import ActiveCall

class ActiveCallRepository:
    def __init__(self) -> None:
        self._lock = Lock()
        self._active: Dict[str, ActiveCall] = {}

    def set(self, phone: str, call: ActiveCall) -> None:
        with self._lock:
            self._active[phone] = call

    def get(self, phone: str) -> Optional[ActiveCall]:
        with self._lock:
            return self._active.get(phone)

    def all_items(self) -> List[ActiveCall]:
        with self._lock:
            return list(self._active.values())

    def remove(self, phone: str) -> None:
        with self._lock:
            self._active.pop(phone, None)

    def find_by_call_id(self, call_id: str) -> Optional[str]:
        """Returns the phone key for a given call_id, if tracked."""
        with self._lock:
            for phone, call in self._active.items():
                if call.call_id == call_id:
                    return phone
        return None

    def clear(self) -> None:
        with self._lock:
            self._active.clear()


active_call_repository = ActiveCallRepository()
