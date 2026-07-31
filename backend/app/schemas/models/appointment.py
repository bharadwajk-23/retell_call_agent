"""Domain model for a booked appointment."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Appointment:
    appointment_id: str
    patient_name: str
    provider_name: str
    phone: Optional[str]
    slot_weekday: Optional[str]
    slot_time: Optional[str]
    notes: Optional[str]
    booked_at: str

    def to_dict(self) -> dict:
        return {
            "appointment_id": self.appointment_id,
            "patient_name": self.patient_name,
            "provider_name": self.provider_name,
            "phone": self.phone,
            "slot_weekday": self.slot_weekday,
            "slot_time": self.slot_time,
            "notes": self.notes,
            "booked_at": self.booked_at,
        }
