"""In-memory appointment store."""

from threading import Lock
from typing import List

from backend.app.models.appointment import Appointment


class AppointmentRepository:
    def __init__(self) -> None:
        self._lock = Lock()
        self._appointments: List[Appointment] = []

    def add(self, appointment: Appointment) -> None:
        with self._lock:
            self._appointments.append(appointment)

    def list_all(self) -> List[Appointment]:
        with self._lock:
            return list(self._appointments)

    def booked_after(self, timestamp: str) -> bool:
        with self._lock:
            return any(a.booked_at >= timestamp for a in self._appointments)

    def clear(self) -> None:
        with self._lock:
            self._appointments.clear()


appointment_repository = AppointmentRepository()
