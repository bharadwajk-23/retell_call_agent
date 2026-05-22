# Retell agent functions — wire these in the dashboard

Expose your backend with a public URL (e.g. ngrok):

```text
https://YOUR-NGROK-ID.ngrok-free.app
```

Use these endpoints as **Custom Functions** on your Retell agent (Response Engine).

---

## 1. Get provider availability

| Field | Value |
|--------|--------|
| **Method** | GET |
| **URL** | `{BASE_URL}/providers/availability?provider_name={provider_name}` |
| **Description** | Returns free appointment slots for the patient's provider. Use when the patient wants to book. |

**Query parameters (tell Retell to pass):**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `provider_name` | string | yes | e.g. `Dr Johnson` — must match `provider_details.json` |

**Example response:**

```json
{
  "provider_name": "Dr Johnson",
  "found": true,
  "free_slots": [
    { "weekday": "Monday", "time": "09:00" },
    { "weekday": "Monday", "time": "11:00" }
  ],
  "message": "42 free slot(s) available"
}
```

**Prompt variables** (set when call starts): `{{patient_name}}`, `{{doctor_name}}`, `{{provider_name}}`, `{{exercise_missed_days}}`, `{{phone}}`

---

## 2. Book appointment

| Field | Value |
|--------|--------|
| **Method** | POST |
| **URL** | `{BASE_URL}/book-appointment` |
| **Content-Type** | `application/json` |
| **Description** | Saves the appointment after the patient picks a weekday and time. |

**JSON body parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `patient_name` | string | yes | From `{{patient_name}}` |
| `provider_name` | string | yes | From `{{provider_name}}` or `{{doctor_name}}` |
| `phone` | string | no | From `{{phone}}` |
| `slot_weekday` | string | yes | e.g. `Monday` |
| `slot_time` | string | yes | e.g. `11:00` |
| `notes` | string | no | Optional |

**Example body:**

```json
{
  "patient_name": "{{patient_name}}",
  "provider_name": "{{provider_name}}",
  "phone": "{{phone}}",
  "slot_weekday": "Monday",
  "slot_time": "11:00"
}
```

**Example response:**

```json
{
  "status": "success",
  "appointment_id": "APT1A2B3C4D",
  "message": "Appointment confirmed for John Smith with Dr Johnson on Monday at 11:00"
}
```

---

## 3. Webhook (events / transcripts)

| Field | Value |
|--------|--------|
| **URL** | `{BASE_URL}/retell-webhook` |
| **Method** | POST |

Configure in Retell **Settings → Webhooks**. Your app appends events to `call_logs.json`; UI reads `GET /transcripts`.

---

## 4. Start call (your app only — not a Retell function)

| Method | URL | Body |
|--------|-----|------|
| POST | `/start-call` | `{"patient_id": 1}` |
| POST | `/make-call` | `{"phone": "+14155550101"}` |

**Env (backend/.env):**

```env
RETELL_API_KEY=...
RETELL_AGENT_ID=...
RETELL_FROM_NUMBER=+1...    # number imported in Retell (Telnyx/Twilio)
RETELL_MOCK_CALLS=false     # true = no real Retell API (local UI testing)
```

**Agent prompt snippet:**

```text
You are a polite physiotherapy clinic assistant.
Greet {{patient_name}}. Mention they missed exercises for {{exercise_missed_days}} days.
Their provider is {{doctor_name}}.
When booking, call get_availability with provider_name={{provider_name}}, then book_appointment with the chosen slot.
Never give medical advice.
```
