"""Domain model for a patient. Kept separate from the API schema in schemas/patient.py."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Patient:
    id: int
    patient_name: str
    phone: str
    dob: str
    provider_name: str
    exercise_missed_days: int
    booking_status: str = "not booked"  # "not booked" | "in progress" | "booked"
    appointment_id: Optional[str] = None

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "patient_name": self.patient_name,
            "phone": self.phone,
            "dob": self.dob,
            "provider_name": self.provider_name,
            "exercise_missed_days": self.exercise_missed_days,
            "booking_status": self.booking_status,
        }
        if self.appointment_id:
            data["appointment_id"] = self.appointment_id
        return data
