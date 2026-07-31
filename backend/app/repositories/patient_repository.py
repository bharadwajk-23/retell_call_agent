"""In-memory patient store.

Patient data is seeded at process start from JSON on disk (see
ProviderRepository for the same pattern) and lives only in memory from then
on (no database). Swapping in a real database later only requires
reimplementing this class.
"""

from threading import Lock
from typing import Any, Dict, List, Optional

from backend.app.core import patient_details_path
from backend.app.schemas.models import Patient
from backend.app.utils import load_json_file, normalize_phone


def _load_seed_patients() -> List[Patient]:
    data = load_json_file(patient_details_path())
    rows: List[Dict[str, Any]] = data if isinstance(data, list) else []
    return [Patient(**row) for row in rows]


class PatientRepository:
    """Thread-safe in-memory patient repository (singleton via app.state)."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._patients: List[Patient] = _load_seed_patients()

    def list_all(self) -> List[Patient]:
        with self._lock:
            return list(self._patients)

    def get_by_id(self, patient_id: int) -> Optional[Patient]:
        with self._lock:
            return next((p for p in self._patients if p.id == patient_id), None)

    def get_by_phone(self, phone: str) -> Optional[Patient]:
        norm = normalize_phone(phone)
        with self._lock:
            return next(
                (p for p in self._patients if normalize_phone(p.phone) == norm), None
            )

    def set_booking_status(self, patient_id: int, status: str) -> None:
        with self._lock:
            for p in self._patients:
                if p.id == patient_id:
                    p.booking_status = status
                    if status != "booked":
                        p.appointment_id = None
                    return

    def mark_booked(self, appointment_id: str, phone: Optional[str], patient_name: str) -> None:
        with self._lock:
            for p in self._patients:
                if phone and normalize_phone(p.phone) == normalize_phone(phone):
                    p.booking_status = "booked"
                    p.appointment_id = appointment_id
                    return
            for p in self._patients:
                if p.patient_name.strip().lower() == patient_name.strip().lower():
                    p.booking_status = "booked"
                    p.appointment_id = appointment_id
                    return

    def reset(self, patient_id: Optional[int] = None) -> None:
        with self._lock:
            for p in self._patients:
                if patient_id is None or p.id == patient_id:
                    p.booking_status = "not booked"
                    p.appointment_id = None


patient_repository = PatientRepository()
