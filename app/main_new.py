"""
FastAPI backend for AI physiotherapy call agent.
"""

import json
import os
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pathlib import Path
import app.config as config
from app.retell_service import trigger_outbound_call, get_call_details

FRONTEND_DIR = Path(__file__).resolve().parent

app = FastAPI(title="AI Physiotherapy Call Agent")

# Serve entire frontend folder
app.mount(
    "/index",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="static"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (no file I/O)
active_calls: Dict[str, Dict[str, Any]] = {}
patients_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "patient_name": "John Smith",
        "phone": "+918147775333",
        "dob": "1988-03-15",
        "provider_name": "Dr Johnson",
        "exercise_missed_days": 5,
        "booking_status": "not booked"
    }
]
appointments_db: List[Dict[str, Any]] = []
call_logs_db: List[Dict[str, Any]] = []


def normalize_phone(phone: str) -> str:
    return re.sub(r"\s+", "", (phone or "").strip())


def load_json_file(file_path: str) -> Any:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_json_file(file_path: str, data: Any) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def append_call_log(log_entry: Dict[str, Any]) -> None:
    call_logs_db.append(log_entry)


def find_patient_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    norm = normalize_phone(phone)
    for p in patients_db:
        if not isinstance(p, dict):
            continue
        if normalize_phone(str(p.get("phone", ""))) == norm:
            return p
    return None


def find_patient_by_id(patient_id: int) -> Optional[Dict[str, Any]]:
    for p in patients_db:
        if not isinstance(p, dict):
            continue
        if p.get("id") == patient_id:
            return p
    return None


CALL_STALE_SECONDS = 20


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _call_is_stale(call_info: Dict[str, Any]) -> bool:
    started_at = _parse_datetime(call_info.get("started_at"))
    if not started_at:
        return False
    return (datetime.now() - started_at).total_seconds() >= CALL_STALE_SECONDS


def _call_is_inactive(call_info: Dict[str, Any]) -> bool:
    if call_info.get("status") in {"completed", "ended", "not_connected", "error"}:
        return True

    call_id = call_info.get("call_id")
    if call_id:
        details = get_call_details(call_id)
        if details:
            details_status = (
                details.get("call_status")
                if isinstance(details, dict)
                else getattr(details, "call_status", None)
            )
            if details_status in {"registered", "ongoing"}:
                return False
            if details_status == "mock":
                return _call_is_stale(call_info)
            if details_status in {"ended", "not_connected", "error"}:
                return True

    return _call_is_stale(call_info)


def _cleanup_active_calls() -> None:
    for phone, call_info in list(active_calls.items()):
        if _call_is_inactive(call_info):
            patient_id = call_info.get("patient_id")
            patient = find_patient_by_id(patient_id) if patient_id is not None else None
            if patient and patient.get("booking_status") == "in progress":
                patient["booking_status"] = "not booked"
            active_calls.pop(phone, None)


def reset_patient_status(patient_id: Optional[int] = None) -> None:
    for p in patients_db:
        if not isinstance(p, dict):
            continue
        if patient_id is None or p.get("id") == patient_id:
            p["booking_status"] = "not booked"
            p.pop("appointment_id", None)


def _call_id_from_response(call_response: Any) -> str:
    cid = getattr(call_response, "call_id", None)
    if cid is None and isinstance(call_response, dict):
        cid = call_response.get("call_id")
    return cid if cid is not None else str(uuid.uuid4())


def _require_from_number() -> str:
    if config.RETELL_MOCK_CALLS:
        return config.RETELL_FROM_NUMBER or "+10000000000"
    if not config.RETELL_FROM_NUMBER:
        raise HTTPException(
            status_code=500,
            detail="RETELL_FROM_NUMBER is not configured (your Telnyx/Twilio number in E.164)",
        )
    return config.RETELL_FROM_NUMBER


def _execute_outbound_call(patient: Dict[str, Any]) -> Dict[str, Any]:
    phone = normalize_phone(str(patient["phone"]))
    from_number = _require_from_number()
    agent_id = config.RETELL_AGENT_ID or None

    call_response = trigger_outbound_call(
        phone_number=phone,
        from_number=from_number,
        patient_name=str(patient.get("patient_name", "")),
        provider_name=str(patient.get("provider_name", "")),
        exercise_missed_days=int(patient.get("exercise_missed_days", 0)),
        agent_id=agent_id,
    )

    if not call_response:
        raise HTTPException(status_code=500, detail="Failed to trigger call")

    call_id = _call_id_from_response(call_response)
    response_status = None
    if isinstance(call_response, dict):
        response_status = call_response.get("call_status")
    else:
        response_status = getattr(call_response, "call_status", None)

    active_calls[phone] = {
        "call_id": call_id,
        "status": response_status or "registered",
        "started_at": datetime.now().isoformat(),
        "phone": phone,
        "patient_name": patient.get("patient_name"),
        "patient_id": patient.get("id"),
    }

    append_call_log(
        {
            "call_id": call_id,
            "phone": phone,
            "patient_id": patient.get("id"),
            "patient_name": patient.get("patient_name"),
            "event": "call_started",
            "timestamp": datetime.now().isoformat(),
            "mock": config.RETELL_MOCK_CALLS,
        }
    )

    return {
        "status": "call generated",
        "call_id": call_id,
        "patient_id": patient.get("id"),
        "patient_name": patient.get("patient_name"),
        "provider_name": patient.get("provider_name"),
        "doctor_name": patient.get("provider_name"),
        "exercise_missed_days": patient.get("exercise_missed_days"),
        "phone": phone,
        "mock": config.RETELL_MOCK_CALLS,
    }


def _free_slots_for_provider(provider_name: str) -> Dict[str, Any]:
    providers: List[Dict[str, Any]] = load_json_file(config.PROVIDER_DETAILS_PATH)
    if not isinstance(providers, list):
        providers = []

    target = None
    for p in providers:
        if not isinstance(p, dict):
            continue
        if str(p.get("provider_name", "")).lower() == provider_name.lower():
            target = p
            break

    if not target:
        return {
            "provider_name": provider_name,
            "found": False,
            "free_slots": [],
            "message": f"No provider named {provider_name}",
        }

    labels = target.get("slot_hour_labels") or config.SLOT_HOUR_LABELS
    weekly = target.get("weekly_availability") or {}
    free_slots: List[Dict[str, str]] = []

    for weekday, slots in weekly.items():
        if not isinstance(slots, list):
            continue
        for i, flag in enumerate(slots):
            if flag == 0 and i < len(labels):
                free_slots.append({"weekday": weekday, "time": labels[i]})

    return {
        "provider_name": target.get("provider_name", provider_name),
        "found": True,
        "free_slots": free_slots,
        "message": f"{len(free_slots)} free slot(s) available",
    }


class MakeCallRequest(BaseModel):
    phone: str = Field(..., description="Patient phone number (E.164 recommended)")


class StartCallRequest(BaseModel):
    patient_id: int = Field(..., description="Patient id from patient_details.json")


class AppointmentRequest(BaseModel):
    patient_name: str
    provider_name: str
    phone: Optional[str] = None
    slot_weekday: Optional[str] = None
    slot_time: Optional[str] = None
    notes: Optional[str] = None


class BookAppointmentRequest(BaseModel):
    """Body shape for Retell custom function POST /book-appointment."""

    patient_name: str
    provider_name: str
    phone: Optional[str] = None
    slot_weekday: str = Field(..., description="e.g. Monday")
    slot_time: str = Field(..., description="e.g. 11:00")
    notes: Optional[str] = None


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "retell_mock_calls": config.RETELL_MOCK_CALLS,
        "from_number_configured": bool(config.RETELL_FROM_NUMBER),
    }


@app.get("/patients")
async def get_patients():
    _cleanup_active_calls()
    return patients_db


@app.post("/reset-patients")
async def reset_patients(patient_id: Optional[int] = None):
    reset_patient_status(patient_id)
    if patient_id is None:
        active_calls.clear()
        appointments_db.clear()
    return {
        "status": "reset",
        "patient_id": patient_id,
        "reset_all": patient_id is None,
    }


@app.post("/start-call")
async def start_call(body: StartCallRequest):
    """Start outbound call by patient id (matches common Retell tutorial flow)."""
    patient = find_patient_by_id(body.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Mark patient as "in progress" when call starts (in-memory)
    patient["booking_status"] = "in progress"
    try:
        return _execute_outbound_call(patient)
    except Exception:
        patient["booking_status"] = "not booked"
        raise


@app.post("/make-call")
async def make_call(body: MakeCallRequest):
    """Start outbound call by phone number."""
    patient = find_patient_by_phone(body.phone)
    if not patient:
        raise HTTPException(
            status_code=404, detail="Patient not found for phone number"
        )
    return _execute_outbound_call(patient)


@app.get("/providers/availability")
async def get_provider_availability(
    provider_name: Optional[str] = Query(
        None,
        description="Filter to one provider; omit for all provider records",
    ),
):
    """
    Retell tool: list free slots (0=free, 1=booked) for a provider.
    Use ?provider_name=Dr Johnson when configuring the agent function.
    """
    if provider_name:
        return _free_slots_for_provider(provider_name)

    providers: List[Dict[str, Any]] = load_json_file(config.PROVIDER_DETAILS_PATH)
    if not isinstance(providers, list):
        return {"providers": []}

    summaries = []
    for p in providers:
        if not isinstance(p, dict):
            continue
        name = str(p.get("provider_name", ""))
        if name:
            summaries.append(_free_slots_for_provider(name))

    return {"providers": summaries}


@app.post("/appointments")
async def save_appointment(appointment: AppointmentRequest):
    return _book_appointment_record(
        patient_name=appointment.patient_name,
        provider_name=appointment.provider_name,
        phone=appointment.phone,
        slot_weekday=appointment.slot_weekday,
        slot_time=appointment.slot_time,
        notes=appointment.notes,
    )

@app.post("/book-appointment")
async def book_appointment(request:Request):
    """
    Retell tool: book an appointment (alias with required slot fields).
    """
    body = await request.json()
    print("--------------")
    print("Received body:", body)
    print("--------------")

    return _book_appointment_record(
        patient_name=body.get("patient_name", ""),
        provider_name=body.get("provider_name", "Bharadwaj"),
        phone=body.get("phone"),
        slot_weekday=body.get("slot_weekday","Monday"),
        slot_time=body.get("slot_time","09:00 am"),
        notes=body.get("notes"),
    )


def _book_appointment_record(
    patient_name: str,
    provider_name: str,
    phone: Optional[str],
    slot_weekday: Optional[str],
    slot_time: Optional[str],
    notes: Optional[str],
) -> Dict[str, Any]:
    record = {
        "appointment_id": f"APT{uuid.uuid4().hex[:8].upper()}",
        "patient_name": patient_name,
        "provider_name": provider_name,
        "phone": phone,
        "slot_weekday": slot_weekday,
        "slot_time": slot_time,
        "notes": notes,
        "booked_at": datetime.now().isoformat(),
    }
    appointments_db.append(record)

    append_call_log(
        {
            "event": "appointment_booked",
            "timestamp": datetime.now().isoformat(),
            "appointment_id": record["appointment_id"],
            "patient_name": patient_name,
            "provider_name": provider_name,
            "slot_weekday": slot_weekday,
            "slot_time": slot_time,
        }
    )

    # Update patient booking status in memory
    for p in patients_db:
        if not isinstance(p, dict):
            continue
        # Prefer matching by phone when available
        if phone and normalize_phone(str(p.get("phone", ""))) == normalize_phone(str(phone)):
            p["booking_status"] = "booked"
            p["appointment_id"] = record["appointment_id"]
            break
        # Fallback to matching by patient name
        if str(p.get("patient_name", "")).strip().lower() == patient_name.strip().lower():
            p["booking_status"] = "booked"
            p["appointment_id"] = record["appointment_id"]
            break

    return {
        "status": "success",
        "appointment_id": record["appointment_id"],
        "message": (
            f"Appointment confirmed for {patient_name} with {provider_name} "
            f"on {slot_weekday} at {slot_time}"
        ),
        "appointment": record,
    }


@app.get("/appointments")
async def list_appointments():
    return appointments_db


@app.post("/retell-webhook")
async def retell_webhook(request: Request):
    try:
        payload = await request.json()
        event = payload.get("event")
        call_id = payload.get("call_id")
        data = payload.get("data", payload)

        log_entry: Dict[str, Any] = {
            "call_id": call_id,
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        if isinstance(data, dict):
            transcript = data.get("transcript") or data.get("transcript_text")
            if transcript:
                log_entry["transcript"] = transcript

        append_call_log(log_entry)

        if event == "call_ended":
            for key, call_info in list(active_calls.items()):
                if call_info.get("call_id") == call_id:
                    call_info["status"] = "completed"
                    call_info["ended_at"] = datetime.now().isoformat()
                    
                    # Check if an appointment was booked during this call
                    patient_id = call_info.get("patient_id")
                    call_start_time = call_info.get("started_at")
                    
                    appointment_booked = False
                    if patient_id and call_start_time:
                        for apt in appointments_db:
                            if isinstance(apt, dict) and apt.get("appointment_id"):
                                apt_time = apt.get("booked_at", "")
                                # Check if appointment was booked after this call started
                                if apt_time >= call_start_time:
                                    appointment_booked = True
                                    break
                    
                    # Reset patient status if no appointment was booked
                    if not appointment_booked:
                        for p in patients_db:
                            if isinstance(p, dict) and p.get("id") == patient_id:
                                p["booking_status"] = "not booked"
                                break
                    
                    active_calls.pop(key, None)
                    break

        return {"status": "received"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )


@app.get("/call-status")
async def get_call_status(phone: str = Query(..., description="Patient phone number")):
    key = normalize_phone(phone)
    if key not in active_calls:
        raise HTTPException(status_code=404, detail="No active call found")
    return active_calls[key]


@app.get("/transcripts")
async def get_transcripts():
    return {"transcripts": call_logs_db}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
