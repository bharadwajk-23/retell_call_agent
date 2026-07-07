"""Domain models for in-flight calls and call/event log entries."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ActiveCall:
    call_id: str
    status: str
    started_at: str
    phone: str
    patient_name: Optional[str]
    patient_id: Optional[int]
    ended_at: Optional[str] = None

    def to_dict(self) -> dict:
        data = {
            "call_id": self.call_id,
            "status": self.status,
            "started_at": self.started_at,
            "phone": self.phone,
            "patient_name": self.patient_name,
            "patient_id": self.patient_id,
        }
        if self.ended_at:
            data["ended_at"] = self.ended_at
        return data


@dataclass
class CallLogEntry:
    event: str
    timestamp: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"event": self.event, "timestamp": self.timestamp, **self.payload}
