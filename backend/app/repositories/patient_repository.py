"""In-memory patient store.

This mirrors the previous application's behaviour exactly: patient data is
seeded at process start and lives only in memory (no database). Swapping in
a real database later only requires reimplementing this class.
"""

from threading import Lock
from typing import List, Optional

from backend.app.models.patient import Patient
from backend.app.utils.phone import normalize_phone

_SEED_PATIENTS: List[Patient] = [
    Patient(
        id=1,
        patient_name="Dave Vipul",
        phone="+918147775334",
        dob="1988-03-15",
        provider_name="Dr Johnson",
        exercise_missed_days=5,
        booking_status="not booked",
    ),
    Patient(
        id=2,
        patient_name="Emiley Davis",
        phone="+918688178501",
        dob="1985-06-20",
        provider_name="Dr Johnson",
        exercise_missed_days=7,
        booking_status="not booked",
    ),
    Patient(
        id=3,
        patient_name="Robert Brown",
        phone="+919099156582",
        dob="1990-02-05",
        provider_name="Dr Johnson",
        exercise_missed_days=10,
        booking_status="not booked",
    ),
]


class PatientRepository:
    """Thread-safe in-memory patient repository (singleton via app.state)."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._patients: List[Patient] = [
            Patient(**p.__dict__) for p in _SEED_PATIENTS
        ]

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
