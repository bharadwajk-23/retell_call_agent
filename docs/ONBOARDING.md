# Onboarding Guide — AI Physiotherapy Call Agent

This document explains the entire codebase, file by file and function by
function, for someone who has never seen this project before. Read it top to
bottom once, then use the "End-to-end flows" section as your map whenever
you're tracing a specific feature.

## 1. What this project does

A clinic has patients who missed their prescribed home exercises. A staff
member opens a dashboard, sees the list of those patients, and clicks
**Start Call** next to one. The backend tells **Retell AI** (a voice-AI
phone-call platform) to place an outbound call to that patient. Retell's
voice agent talks to the patient using a prompt configured in Retell's own
dashboard (not in this repo), and — if the patient agrees to a slot — the
agent calls back into *this* backend mid-conversation to check availability
and book the appointment. The dashboard polls the backend every 2 seconds so
the button's label updates live: **Start Call → Calling… → Booked**.

There is **no inbound calling** (nothing here answers a phone call) and
**no database** (everything lives in memory and resets when the process
restarts, or on demand via the Reset button).

## 2. The two halves of the repo

```
retell_call_agent/
├── backend/     FastAPI service — all business logic, in-memory data, Retell integration
├── frontend/    React (Vite) dashboard — the UI described above
├── docs/        this file, plus deployment/setup notes
├── docker-compose.yml   runs both together
├── .env / .env.example  single shared config file for both services
└── README.md
```

The backend never serves the frontend and knows nothing about React; the
frontend only ever talks to the backend over HTTP (`fetch`), via
`VITE_API_BASE_URL`.

---

## 3. Backend — request flow in one picture

```
HTTP request
   │
   ▼
main.py (creates the FastAPI app, wires middleware + routers)
   │
   ▼
middleware/  (runs on every request: logging, then error handling)
   │
   ▼
routers/     (one file per resource — validates input, calls a service, returns the result)
   │
   ▼
services/    (business logic — the only layer allowed to make decisions)
   │
   ├──▶ repositories/   (in-memory data: patients, active calls, appointments, call log)
   └──▶ clients/        (talks to the real Retell AI SDK)
   │
   ▼
schemas/     (Pydantic models define the exact JSON shape in/out of every router)
core/        (settings, constants, logging, webhook-signature security — used by everything above)
```

`models/` (plain dataclasses) sit next to `repositories/` — they're the
in-memory *domain* objects, distinct from `schemas/` (the *API* contract).

---

## 4. Backend, folder by folder, file by file

### 4.1 `backend/app/main.py` — the entrypoint

- **`lifespan(app)`** — an async context manager FastAPI runs once at
  startup and once at shutdown. On startup it logs
  `"Starting AI Physiotherapy Call Agent API"` and, if no `RETELL_API_KEY`
  is set, logs a warning (outbound calls would fail). On shutdown it just
  logs a line.
- **`create_app()`** — builds and returns the `FastAPI` instance:
  - Sets title/version from `core/constants.py` (`API_TITLE`, `API_VERSION`);
    `docs_url`/`openapi_url` are FastAPI's own defaults (`/docs`,
    `/openapi.json`) — nothing overrides them.
  - Adds `CORSMiddleware` using `settings.cors_origins_list`.
  - Adds `RequestLoggingMiddleware` (see 4.4).
  - Calls `register_exception_handlers(app)` (see 4.4).
  - Mounts all 6 routers: `health`, `patients`, `calls`, `providers`,
    `appointments`, `webhooks`.
- **`app = create_app()`** — the module-level object uvicorn actually runs
  (`backend.app.main:app`, invoked from the **project root**, not from
  inside `backend/` — that's what makes the `backend.app.*` import style
  resolve; `backend/__init__.py` is what makes `backend` importable as a
  package).
- **`if __name__ == "__main__":`** — lets you run `python -m backend.app.main`
  directly from the project root; reads `HOST`/`PORT` from settings and
  always enables `reload` (this app only ever runs locally).

### 4.2 `backend/app/core/` — the only place allowed to read environment variables

- **`config.py`**
  - `Settings(BaseSettings)` — every environment variable the app reads,
    with defaults and a docstring rule: *nothing else in the project should
    call `os.environ` directly*. Fields: `HOST`, `PORT`, `LOG_LEVEL`,
    `CORS_ORIGINS`, `RETELL_API_KEY`, `RETELL_AGENT_ID`,
    `RETELL_FROM_NUMBER`, `RETELL_WEBHOOK_VERIFY`, `PROVIDER_DETAILS_PATH`,
    `CALL_STALE_SECONDS` (default 20s), `SLOT_HOUR_LABELS` (fallback hour
    labels for provider availability). `extra="ignore"` means unrelated keys
    in `.env` (like the spare `RETELL_AGENT_ID_Backup`) are silently
    ignored, not errors.
  - `Settings.cors_origins_list` (property) — splits `CORS_ORIGINS` on
    commas into a clean list.
  - `get_settings()` — `@lru_cache`'d singleton constructor; this is how
    every other file obtains settings (`get_settings()` always returns the
    same instance, read once from `.env`/the process environment).
  - `BACKEND_DIR`, `DATA_DIR` — filesystem path constants
    (`DATA_DIR = backend/app/data`).
  - `provider_details_path()` — returns `Settings.PROVIDER_DETAILS_PATH` if
    an operator overrode it, otherwise `DATA_DIR / "provider_details.json"`.
- **`constants.py`** — literal values that used to be scattered inline,
  now named in one place: API metadata/URLs for `main.py`;
  `TERMINAL_CALL_STATUSES` / `DETAILS_TERMINAL_STATUSES` /
  `ACTIVE_CALL_STATUSES` for `call_service.py`'s call-lifecycle logic;
  `DEFAULT_PROVIDER_NAME` / `DEFAULT_SLOT_WEEKDAY` / `DEFAULT_SLOT_TIME` —
  the fallback values Retell's booking custom function uses if it omits a
  field (see `schemas/appointment.py`).
- **`logging.py`**
  - `configure_logging()` — sets up one `StreamHandler` to stdout with a
    `timestamp | LEVEL | logger name | message` format, sized to
    `LOG_LEVEL`; guards against adding a second handler on reload; quiets
    `uvicorn.access` in production.
  - `get_logger(name)` — thin wrapper over `logging.getLogger(name)`, used
    everywhere instead of `print()`.
- **`security.py`**
  - `verify_retell_signature(body, secret, signature)` — verifies the
    `x-retell-signature` header on an inbound webhook using Retell's own
    `retell.lib.webhook_auth.verify`. Returns `False` immediately if either
    the signature header or the secret is missing.

### 4.3 `backend/app/clients/retell_client.py` — the only file that talks to the Retell SDK

- **`RetellClient.__init__`** — builds a `retell.Retell(api_key=...)` SDK
  client if `RETELL_API_KEY` is configured; otherwise `self._client` stays
  `None` (every call attempt then fails fast with a logged error instead of
  crashing).
- **`_dynamic_variables(patient_name, provider_name, exercise_missed_days, phone_number)`**
  (static) — builds the dict of variables sent to Retell:
  `patient_name`, `doctor_name`, `provider_name`, `exercise_missed_days`
  (stringified), `phone`. These get substituted into `{{patient_name}}`-style
  placeholders in the agent's prompt, which is configured **in the Retell
  dashboard**, not in this repo.
- **`trigger_outbound_call(phone_number, from_number, patient_name, provider_name, exercise_missed_days, agent_id=None)`**
  — the actual outbound-call trigger. Builds the dynamic variables, then
  calls `self._client.call.create_phone_call(from_number=..., to_number=...,
  retell_llm_dynamic_variables=dynamic_vars, metadata=dynamic_vars,
  override_agent_id=agent_id if provided)`. Returns `None` (logged) if the
  client isn't configured or the SDK call raises.
- **`get_call_details(call_id)`** — calls `self._client.call.retrieve(call_id)`
  to fetch a call's live status from Retell. Returns `None` on any failure.
- **`retell_client = RetellClient()`** — the module-level singleton every
  service imports.

### 4.4 `backend/app/middleware/` — runs on every request, regardless of route

- **`error_handlers.py` → `register_exception_handlers(app)`** — registers
  three FastAPI exception handlers so no endpoint ever leaks a raw
  traceback: `HTTPException` (logs + passes through the status/detail),
  `RequestValidationError` (422 + Pydantic's `.errors()`), and a catch-all
  `Exception` (`logger.exception(...)` + generic 500 `"Internal server error"`).
- **`request_logging.py` → `RequestLoggingMiddleware.dispatch`** — times
  every request, logs `METHOD path -> status (duration ms)` after the
  response is produced.

### 4.5 `backend/app/models/` — in-memory domain objects (plain dataclasses)

- **`patient.py` → `Patient`** — `id`, `patient_name`, `phone`, `dob`,
  `provider_name`, `exercise_missed_days`, `booking_status` (defaults to
  `"not booked"`; the only three values used anywhere are `"not booked"` /
  `"in progress"` / `"booked"`), `appointment_id`. `to_dict()` omits
  `appointment_id` when it's falsy.
- **`call.py` → `ActiveCall`** — one currently-ringing/in-progress call:
  `call_id`, `status`, `started_at`, `phone`, `patient_name`, `patient_id`,
  `ended_at`. `to_dict()` only includes `ended_at` once it's set.
  Also **`CallLogEntry`** — one row in the audit/event log: `event`,
  `timestamp`, `payload` dict; `to_dict()` flattens `payload` into the
  top-level dict alongside `event`/`timestamp`.
- **`appointment.py` → `Appointment`** — `appointment_id`, `patient_name`,
  `provider_name`, `phone`, `slot_weekday`, `slot_time`, `notes`, `booked_at`.

### 4.6 `backend/app/repositories/` — thread-safe in-memory storage

Every repository is a class wrapping a plain Python list/dict guarded by a
`threading.Lock`, exposed as a module-level singleton. No database exists
anywhere in this app.

- **`patient_repository.py`** — seeds 3 hardcoded demo patients
  (`_SEED_PATIENTS`: Dave Vipul, Emiley Davis, Robert Brown, all under
  "Dr Johnson") at process start.
  - `list_all()` / `get_by_id(id)` / `get_by_phone(phone)` (normalizes phone
    before comparing) — reads.
  - `set_booking_status(patient_id, status)` — writes `booking_status`;
    also clears `appointment_id` whenever the new status isn't `"booked"`.
  - `mark_booked(appointment_id, phone, patient_name)` — tries to match the
    patient by phone first, then falls back to a case-insensitive name
    match; sets `booking_status="booked"` and stores the `appointment_id`.
  - `reset(patient_id=None)` — resets one patient (or all, if `None`) back
    to `"not booked"` with no `appointment_id`.
- **`active_call_repository.py`** — dict keyed by normalized phone number.
  `set` / `get` / `all_items` / `remove` / `clear`, plus
  `find_by_call_id(call_id)` (linear scan to map a Retell `call_id` back to
  the phone key — used by the webhook handler, which only knows `call_id`).
- **`appointment_repository.py`** — append-only list. `add` / `list_all` /
  `clear`, plus `booked_after(timestamp)` — "was any appointment booked at
  or after this ISO timestamp?", used to tell whether a call resulted in a
  booking.
- **`call_log_repository.py`** — append-only audit log of every call/webhook
  event (`append`, `list_all`); this is what `GET /calls/transcripts` returns.
- **`provider_repository.py`** — **not in-memory seeded data** — reads
  `provider_details.json` fresh from disk on every call via
  `utils.json_files.load_json_file` (no caching). `list_all()` returns the
  raw list of provider dicts; `get_by_name(name)` does a case-insensitive
  linear scan.

### 4.7 `backend/app/data/provider_details.json`

Static reference data — availability grids for two providers, "Dr Johnson"
and "Dr Williams". Each entry has `provider_name`, `slot_hour_labels` (10
human-readable time labels), and `weekly_availability` (a dict of weekday →
10-element array of `0`=free/`1`=booked flags, positionally matched to
`slot_hour_labels`).

### 4.8 `backend/app/schemas/` — the exact JSON shape of every request/response

One module per resource, all plain Pydantic `BaseModel`s (no logic):

- **`common.py`** — `ErrorResponse` (`detail`), `HealthResponse`
  (`status`, `from_number_configured`), `ReadinessResponse` (`status`,
  optional `reason`).
- **`patient.py`** — `PatientOut` (mirrors `Patient.to_dict()`),
  `ResetPatientsResponse` (`status`, `patient_id`, `reset_all`).
- **`call.py`** — `StartCallRequest` (`patient_id`), `MakeCallRequest`
  (`phone`), `CallResponse` (the shape returned right after triggering a
  call), `ActiveCallStatus` (mirrors `ActiveCall.to_dict()`),
  `TranscriptsResponse` (`transcripts: list`).
- **`provider.py`** — `FreeSlot` (`weekday`, `time`), `ProviderAvailability`
  (one provider's free slots), `ProvidersAvailabilityResponse` (all
  providers, when no filter is given).
- **`appointment.py`** — `AppointmentRequest` (generic booking body),
  `BookAppointmentRequest` (the shape **Retell's booking custom function**
  sends — defaults `provider_name`/`slot_weekday`/`slot_time` from
  `core/constants.py` so the existing Retell agent config keeps working
  even if it omits those fields), `AppointmentOut`, `BookAppointmentResponse`.
- **`webhook.py`** — `RetellWebhookPayload` (`extra="allow"` — Retell's
  webhook body shape varies per event, so only `event`/`call_id`/`data` are
  declared and everything else passes through untouched), `WebhookAck`
  (`status`).

### 4.9 `backend/app/routers/` — HTTP layer only (validate → call a service → return)

- **`health.py`**
  - `GET /health` → always `{"status": "ok", "from_number_configured": bool}`.
  - `GET /ready` → delegates to `health_service.check_readiness()`.
- **`patients.py`**
  - `GET /patients` → `patient_service.list_patients()`, wrapped one-by-one
    into `PatientOut`.
  - `POST /patients/reset` → `patient_service.reset_patients(patient_id)`.
- **`calls.py`**
  - `POST /calls/start` → `call_service.start_call(patient_id)` — the
    dashboard's **Start Call** button.
  - `POST /calls/make` → `call_service.make_call(phone)` — same thing, by
    phone number instead of patient id (not currently used by the frontend).
  - `GET /calls/status` → `call_service.get_call_status(phone)`.
  - `GET /calls/transcripts` → `call_service.list_transcripts()`.
- **`providers.py`**
  - `GET /providers/availability` → `provider_service.get_availability(provider_name)`
    — this is one of the two **Retell custom functions** the voice agent
    calls mid-conversation to check free slots.
- **`appointments.py`**
  - `POST /appointments` → generic booking via `AppointmentRequest`.
  - `POST /appointments/book` → **the other Retell custom function** — books
    the slot the patient agreed to during the call.
  - `GET /appointments` → `appointment_service.list_appointments()`.
- **`webhooks.py`**
  - `POST /webhooks/retell` — Retell calls this to report call lifecycle
    events. Reads the raw body + `x-retell-signature` header, calls
    `webhook_service.verify_signature(body, signature)` (raises 401 if
    `RETELL_WEBHOOK_VERIFY=true` and the signature is missing/invalid; a
    no-op otherwise), then `webhook_service.handle_webhook(payload)`.

### 4.10 `backend/app/services/` — all business logic lives here

- **`health_service.py` → `check_readiness()`** — `"not_ready"` (with a
  reason) if `RETELL_FROM_NUMBER` isn't configured, else `"ready"`.
- **`patient_service.py`**
  - `list_patients()` — runs `call_service.cleanup_active_calls()` first
    (as a side effect of every list call — this is what keeps
    `booking_status` accurate; see the polling flow below), then returns
    `patient_repository.list_all()`.
  - `reset_patients(patient_id=None)` — resets the patient repo; if
    resetting *all* patients (`patient_id is None`), also clears
    `active_call_repository` and `appointment_repository` entirely.
- **`provider_service.py`**
  - `_free_slots_for_provider(provider_name)` — looks the provider up; if
    not found, returns a `found=False` stub. Otherwise walks
    `weekly_availability`, and for every `0` (free) flag builds a
    `{weekday, time}` entry using that provider's own `slot_hour_labels` (or
    the global `settings.SLOT_HOUR_LABELS` fallback if the provider record
    omits them).
  - `get_availability(provider_name)` — if a name is given, returns that
    provider's slots; otherwise returns every provider's slots under
    `{"providers": [...]}`.
- **`appointment_service.py`**
  - `book_appointment(patient_name, provider_name, phone, slot_weekday, slot_time, notes)`
    — generates `appointment_id = f"APT{uuid4().hex[:8].upper()}"`, saves an
    `Appointment` record, logs an `"appointment_booked"` event, calls
    `patient_repository.mark_booked(...)`, and returns a confirmation
    message plus the full appointment record.
  - `list_appointments()` — returns every booked appointment as dicts.
- **`webhook_service.py`**
  - `verify_signature(body, signature)` — the router-fix described in
    section 4.9; no-op unless `RETELL_WEBHOOK_VERIFY` is on.
  - `handle_webhook(payload)` — logs every event to `call_log_repository`
    (pulling out a transcript field if present). On a `"call_ended"` event:
    finds the phone by `call_id`, marks the `ActiveCall` `status="completed"`
    + `ended_at`, checks `appointment_repository.booked_after(call.started_at)`
    to decide whether *this* call resulted in a booking, resets
    `booking_status` back to `"not booked"` if not, then **removes** the
    call from `active_call_repository`.
- **`call_service.py`** — the largest and most important service:
  - `_require_from_number()` — raises 500 if `RETELL_FROM_NUMBER` isn't
    configured; otherwise returns it.
  - `_call_id_from_response(call_response)` / `_status_from_response(call_response)`
    — small adapters, since the Retell SDK sometimes returns an object and
    sometimes a dict; falls back to a random UUID if no `call_id` is present.
  - `_execute_outbound_call(patient)` — the shared core of both call-start
    paths: normalizes the phone, requires a from-number, calls
    `retell_client.trigger_outbound_call(...)`; on failure raises 500
    `"Failed to trigger call"`. On success: registers an `ActiveCall`
    (status defaults to `"registered"` if Retell's response doesn't say
    otherwise), appends a `"call_started"` log event, and returns the
    response body the router sends back to the frontend.
  - `start_call(patient_id)` — looks the patient up (404 if missing), sets
    `booking_status="in progress"` **before** dialing, calls
    `_execute_outbound_call`, and rolls the status back to `"not booked"` if
    anything raised.
  - `make_call(phone)` — same as above but looked up by phone, without the
    booking-status bookkeeping (used by the phone-based entrypoint).
  - `get_call_status(phone)` — 404s if there's no active call for that
    phone, otherwise returns the `ActiveCall` as a dict.
  - `_call_is_stale(call)` — `True` if the call started more than
    `CALL_STALE_SECONDS` (default 20s) ago and we still have no clearer
    signal.
  - `_call_is_inactive(call)` — the heart of the cleanup logic: if our own
    cached `status` is already terminal (`TERMINAL_CALL_STATUSES`), it's
    inactive. Otherwise it asks Retell directly
    (`retell_client.get_call_details(call.call_id)`) for the live status: if
    that's `"registered"`/`"ongoing"` (`ACTIVE_CALL_STATUSES`) it's still
    active; if it's `"ended"`/`"not_connected"`/`"error"`
    (`DETAILS_TERMINAL_STATUSES`) it's inactive; otherwise it falls back to
    the staleness check.
  - `cleanup_active_calls()` — iterates every active call; for each inactive
    one, resets the patient's `booking_status` back to `"not booked"` **if**
    it was still `"in progress"` (a booked call is left alone), then removes
    it from `active_call_repository`. **This runs on every `GET /patients`
    call** — see the polling flow below for why that matters.
  - `list_transcripts()` — the whole call/webhook event log, dict-ified.

### 4.11 `backend/app/utils/` — generic, stateless helpers

- **`json_files.py` → `load_json_file(path)`** — reads and parses a JSON
  file; returns `[]` (logged) on `FileNotFoundError` or invalid JSON, rather
  than raising.
- **`phone.py` → `normalize_phone(phone)`** — strips whitespace so phone
  numbers compare reliably regardless of formatting.

### 4.12 Every `__init__.py`

Every package has one, and none contain logic — they only re-export the
public names of that package (e.g. `backend/app/repositories/__init__.py`
exposes all 5 repository singletons) so callers can write
`from backend.app.repositories import patient_repository` if they prefer,
though most of the codebase imports the specific submodule directly.

---

## 5. Frontend, file by file

React + Vite dashboard. Nothing here talks to Retell directly — it only
calls this backend's HTTP API.

### 5.1 Bootstrapping

- **`main.jsx`** — mounts `<App />` into `#root` inside `<StrictMode>`.
- **`App.jsx`** — wraps everything in `<PatientsProvider>` and renders
  `<Dashboard />`. That's the entire component tree's root.

### 5.2 State layer (`context/` + `hooks/`)

This is a small Context + custom-hook state manager — no Redux/Zustand.

- **`hooks/usePatientsData.js`** — **the one hook that owns all state and
  side effects**:
  - `loadPatients({skipLoading})` — calls `getPatients()`, stores the array,
    clears/sets `error`.
  - A `useEffect` on mount starts `window.setInterval(refreshPatients, POLL_INTERVAL_MS)`
    (2000ms, from `constants/config.js`) — this is **the poll** the whole
    live-status experience is built on. Cleared on unmount.
  - `handleStartCall(patientId)` — sets `pendingId` (disables that row's
    button + shows "Starting…"), calls `startCall(patientId)`, immediately
    reloads the patient list afterward, clears `pendingId` in a `finally`.
  - `handleReset()` — calls `resetPatients()`, then reloads the list.
  - Returns `{patients, loading, error, pendingId, startCall, resetDemo, dismissError}`.
- **`context/patientsContext.js`** — just `export const PatientsContext = createContext(null)`,
  kept in its own file (not the `.jsx` one) so Vite's Fast Refresh doesn't
  break — a file that exports a component must only export components.
- **`context/PatientsContext.jsx` → `PatientsProvider`** — calls
  `usePatientsData()` once and provides its return value down the tree.
- **`hooks/usePatients.js`** — the *consumer* hook every component actually
  uses (`useContext(PatientsContext)`); throws if used outside the
  provider, which would be a bug, not a normal condition.
- **`hooks/useTimeOfDay.js`** — unrelated to patients; computes
  morning/afternoon/evening/night for the greeting banner's icon/greeting
  text, rechecking every 60s, with a `?tod=morning` URL override for
  previewing every state on demand.

### 5.3 API layer (`services/api/`)

- **`client.js` → `apiRequest(path, options)`** — the only place `fetch()`
  is called anywhere in the app. Prefixes `VITE_API_BASE_URL` (or `/api`),
  always sends `Content-Type: application/json`, parses JSON or text based
  on the response's content-type, and throws an `Error` (using the
  response's `detail` field if present) on any non-2xx status.
- **`patients.js`** — `getPatients()` → `GET /patients`; `resetPatients()`
  → `POST /patients/reset`.
- **`calls.js`** — `startCall(patientId)` → `POST /calls/start` with
  `{patient_id: patientId}`.
- **`index.js`** — a barrel file re-exporting `getPatients`,
  `resetPatients`, `startCall` so components import from
  `'../services/api'` instead of individual files.

### 5.4 Presentation helpers (`utils/`, `constants/`)

- **`constants/config.js`** — `POLL_INTERVAL_MS=2000`,
  `URGENT_MISSED_DAYS_THRESHOLD=10`, `BOOKING_STATUS` string constants
  (`"not booked"` / `"in progress"` / `"booked"` — must match the backend's
  `booking_status` values exactly, since nothing enforces that
  cross-language contract except convention).
- **`utils/status.js` → `getBookingStatusMeta(bookingStatus)`** — maps a
  patient's `booking_status` to a `{status, label, variant, disabled}`
  object the button renders from: `"in progress"` → "Calling…" (disabled),
  `"booked"` → "Booked" (disabled), anything else → "Start Call" (enabled).
- **`utils/severity.js`** — `getMissedDaysSeverity(missedDays)` (≥10 days →
  `"urgent"`, else `"follow-up"`, purely a display label — the threshold is
  never sent to the backend); `formatPatientCode(id)` (cosmetic `P-1041`
  style code); `getInitials(name)` (avatar initials).

### 5.5 Components (all presentational, no direct API calls)

- **`components/Navbar/Navbar.jsx`** — brand, search input (with a
  Cmd/Ctrl+K shortcut to focus it), and the **Reset** button
  (`onReset` passed down from `Dashboard`).
- **`components/GreetingBanner/GreetingBanner.jsx`** — time-of-day greeting
  + "You have N patients who missed exercises" copy.
- **`components/PatientTable/PatientTable.jsx`** — renders one row per
  patient: avatar/initials, name, patient code, phone, DOB, a
  `SeverityPill` for missed days, provider name, and a `CallActionButton`.
- **`components/CallActionButton/CallActionButton.jsx`** — the actual
  **Start Call** button; purely derives its label/disabled state from
  `getBookingStatusMeta` plus the `pending` flag (mid-request).
- **`components/SeverityPill/SeverityPill.jsx`** — small colored pill
  ("Urgent" / "Follow-up").
- **`components/ErrorBanner/ErrorBanner.jsx`** — dismissible error banner,
  renders `null` if there's no message.
- **`components/EmptyState/EmptyState.jsx`** — "No patients found" /
  "No matches" placeholder.
- **`components/TableSkeleton/TableSkeleton.jsx`** — loading-state
  placeholder rows.
- **`components/Footer/Footer.jsx`** — static copyright line.

### 5.6 `pages/Dashboard/Dashboard.jsx` — ties it all together

Reads `{patients, loading, error, pendingId, startCall, resetDemo, dismissError}`
from `usePatients()`, filters the list client-side by `searchTerm` (name,
phone, or provider substring match via `matchesSearch`), computes
`activeCount` (patients not yet `"booked"`) and a `doctorName` for the
greeting, and renders: `Navbar` → `GreetingBanner` → optional `ErrorBanner`
→ (`TableSkeleton` while loading, `EmptyState` if the filtered list is
empty, or `PatientTable` otherwise) → `Footer`.

---

## 6. End-to-end flows — the part that matters most

### 6.1 App startup

1. **Backend**: `uvicorn backend.app.main:app` (run from the project root)
   imports `main.py` → module-level `configure_logging()` runs →
   `app = create_app()` builds the FastAPI app, registers
   middleware/exception handlers, mounts routers →
   `lifespan()`'s startup half logs the boot line.
2. **Frontend**: Vite serves `main.jsx` → `App.jsx` → `PatientsProvider`
   calls `usePatientsData()`, which immediately fires `loadPatients()` (shows
   the loading skeleton) and starts the 2-second polling interval.

### 6.2 "Start Call" — the primary flow

1. User clicks **Start Call** on a patient row → `CallActionButton`'s
   `onClick` → `Dashboard`'s `onStartCall(patient.id)` → context's
   `startCall` → `usePatientsData.handleStartCall(patientId)`.
2. Frontend sets `pendingId`, calls `startCall(patientId)` →
   `POST /calls/start {"patient_id": ...}`.
3. Backend: `routers/calls.py::start_call` → `call_service.start_call(patient_id)`.
4. `call_service` looks up the patient (404 if missing), immediately sets
   `booking_status="in progress"` — this is what the very next poll will
   render as "Calling…" — then calls `_execute_outbound_call(patient)`.
5. `_execute_outbound_call` gets `RETELL_FROM_NUMBER`, calls
   `retell_client.trigger_outbound_call(...)` — this hits the real Retell
   SDK's `call.create_phone_call(...)`, sending `patient_name`,
   `doctor_name`/`provider_name`, `exercise_missed_days`, `phone` as dynamic
   variables so Retell's agent prompt (configured in Retell's dashboard) can
   reference them.
6. On success: an `ActiveCall` is stored (keyed by phone), a
   `"call_started"` event is appended to the call log, and a `CallResponse`
   body goes back to the frontend. On failure: a 500 is raised, which rolls
   `booking_status` back to `"not booked"` and surfaces `error` in the UI.
7. Frontend's `handleStartCall` reloads the patient list right after the
   request resolves (regardless of outcome), so the UI reflects "in
   progress" (or the rolled-back "not booked" on failure) immediately, not
   after the next poll tick.

### 6.3 While the call is ongoing — the 2-second poll

1. Every 2 seconds, `usePatientsData`'s interval calls `getPatients()` →
   `GET /patients`.
2. `routers/patients.py::get_patients` → `patient_service.list_patients()`,
   which **first** runs `call_service.cleanup_active_calls()` — this is the
   mechanism that keeps `booking_status` live, not a separate
   `/calls/status` poll.
3. `cleanup_active_calls` asks Retell directly
   (`retell_client.get_call_details`) for every active call's real status.
   If a call is still ongoing, nothing changes. If it's ended (or 20+
   seconds stale with no clear signal), the patient's `booking_status` is
   reset to `"not booked"` **unless** it's already `"booked"` (a successful
   booking is never undone by this path) — then the call is removed from
   `active_call_repository`.
4. `patient_repository.list_all()` is returned, serialized as `PatientOut[]`.
5. Frontend re-renders: the button goes from "Calling…" back to "Start
   Call" (if nothing was booked) automatically on the next poll after the
   call actually ends — no extra wiring needed on the frontend side.

### 6.4 Booking happens *during* the call (Retell custom functions)

1. While talking to the patient, Retell's agent (per its own dashboard
   prompt/config) calls **your API as a function**, not this frontend:
   `GET /providers/availability?provider_name=...` →
   `provider_service.get_availability` → reads `provider_details.json`,
   returns free slots.
2. Once the patient agrees to a slot, the agent calls the other custom
   function: `POST /appointments/book` (defaults for
   `provider_name`/`slot_weekday`/`slot_time` come from `core/constants.py`
   if the agent's function call omits them) →
   `appointment_service.book_appointment`.
3. That creates the `Appointment` record, logs an `"appointment_booked"`
   event, and — critically — calls `patient_repository.mark_booked(...)`,
   which flips `booking_status` to `"booked"` immediately (matched by phone,
   falling back to name).
4. The very next 2-second poll (6.3) picks this up: `cleanup_active_calls`
   sees the patient is no longer `"in progress"` so it leaves it alone, and
   the frontend renders "Booked".

### 6.5 Call-ended webhook (belt-and-suspenders, not the primary signal)

1. Retell also POSTs lifecycle events to `POST /webhooks/retell`
   independently of anything the frontend is doing.
2. `routers/webhooks.py::retell_webhook` reads the raw body + signature
   header, calls `webhook_service.verify_signature` (only enforced if
   `RETELL_WEBHOOK_VERIFY=true`), then `webhook_service.handle_webhook(payload)`.
3. Every event is logged to `call_log_repository` regardless of type
   (visible via `GET /calls/transcripts`).
4. On `"call_ended"`: finds the active call by `call_id`, marks it
   `status="completed"`, checks whether an appointment was booked at/after
   the call's start time, resets `booking_status` to `"not booked"` if not,
   and removes the active call.
5. This overlaps with 6.3's polling-based cleanup — either one can resolve
   the "not booked" fallback first; both are idempotent (a `"booked"`
   patient is left alone by both paths), so there's no race condition that
   corrupts state, only redundancy for reliability if Retell's webhook is
   slow/unconfigured.

### 6.6 Reset

1. User clicks **Reset** in the `Navbar` → `Dashboard`'s `resetDemo` →
   `usePatientsData.handleReset` → `resetPatients()` → `POST /patients/reset`.
2. `routers/patients.py::reset_patients` → `patient_service.reset_patients(None)`
   (no `patient_id` query param from this button, so it resets *all*).
3. `patient_repository.reset(None)` sets every patient back to
   `"not booked"` with no `appointment_id`; because `patient_id is None`,
   `reset_patients` also calls `active_call_repository.clear()` and
   `appointment_repository.clear()` — every in-flight call and every booked
   appointment is wiped.
4. Frontend reloads the patient list right after — every row shows "Start
   Call" again, exactly like a fresh process start (except the call log in
   `call_log_repository` is *not* cleared by reset — it's a permanent audit
   trail for the process lifetime).

---

## 7. Configuration reference (`.env`)

| Variable | Read by | Purpose |
|---|---|---|
| `HOST` / `PORT` | `main.py` (`__main__` runner) | uvicorn bind address |
| `LOG_LEVEL` | `core/logging.py` | Python logging level |
| `CORS_ORIGINS` | `main.py` (CORS middleware) | comma-separated allowed frontend origins |
| `RETELL_API_KEY` | `clients/retell_client.py`, `core/security.py` | Retell SDK auth + webhook signature secret |
| `RETELL_AGENT_ID` | `call_service.py` | optional `override_agent_id` on outbound calls |
| `RETELL_FROM_NUMBER` | `call_service.py`, `health_service.py` | your Telnyx/Twilio number in E.164 — required for calls to work and for `/ready` to report ready |
| `RETELL_WEBHOOK_VERIFY` | `webhook_service.py` | off by default; turn on once you've confirmed Retell's signing header for your account |
| `PROVIDER_DETAILS_PATH` | `core/config.py` | override the default `app/data/provider_details.json` path |
| `CALL_STALE_SECONDS` | `call_service.py` | staleness fallback when Retell's own status is ambiguous (default 20s) |
| `VITE_API_BASE_URL` | frontend `client.js` | backend base URL, baked in at frontend build time |
| `FRONTEND_PORT` / `BACKEND_PORT` | `docker-compose.yml` | host-side port mapping only |

`RETELL_AGENT_ID_Backup` currently exists in `.env` but is not read anywhere
in the code (`Settings` uses `extra="ignore"`, so it's silently unused —
not a bug, just an unwired spare value).

---

## 8. Quick reference — "I want to change X, where do I look?"

| I want to... | Look at |
|---|---|
| Change what data gets sent to Retell when a call starts | `clients/retell_client.py::_dynamic_variables` |
| Change when a patient's booking status reverts to "not booked" | `services/call_service.py::_call_is_inactive` / `cleanup_active_calls` |
| Add a new field to the patient list API | `models/patient.py`, `schemas/patient.py`, `repositories/patient_repository.py` |
| Add a new outbound-call trigger reason | `services/call_service.py::_execute_outbound_call` (shared by `start_call`/`make_call`) |
| Change provider availability data | `data/provider_details.json` |
| Add a new Retell custom function | new router + service function, mirroring `routers/appointments.py::book_appointment` |
| Change how often the dashboard polls | `frontend/src/constants/config.js::POLL_INTERVAL_MS` |
| Change the "urgent" threshold on the dashboard | `frontend/src/constants/config.js::URGENT_MISSED_DAYS_THRESHOLD` |
| Add a new environment variable | `backend/app/core/config.py::Settings` (nowhere else should read `os.environ`) |
| Add a new hardcoded literal that's used in 2+ places | `backend/app/core/constants.py` |

---

## 9. Running it locally

### 9.1 Prerequisites

- Python 3.11+
- Node.js 18+ / npm
- A Retell AI account + API key if you want the "Start Call" button to place
  real calls (see `docs/RETELL_SETUP.md`) — without one, the backend still
  runs, but `_require_from_number`/`trigger_outbound_call` will fail calls
  with a clear error instead of silently doing nothing.

### 9.2 One-time setup

```bash
cp .env.example .env   # fill in RETELL_API_KEY, RETELL_AGENT_ID, RETELL_FROM_NUMBER, etc.
./initialize.sh        # creates backend/venv + frontend/venv, installs both sets of dependencies
```

`initialize.sh` only installs dependencies — it never touches `.env`, never
builds the frontend, and never starts anything. Concretely, per half of the
repo: `python3 -m venv backend/venv` (if missing) + `pip install -r
backend/requirements.txt`; then `npm install` in `frontend/`, plus a second
small `frontend/venv` used only to *serve* the built frontend later (9.4B).

### 9.3 Running the backend

**Scripted (recommended for day-to-day use):**

```bash
./start_backend.sh
```

This reads `HOST`/`PORT` from the root `.env`, activates `backend/venv`, and
runs uvicorn **from the project root** with `--reload` always on (this app
only ever runs locally). Comes up on `http://localhost:8006` (Swagger UI at
`/docs`).

**Manual equivalent** (same thing, spelled out — useful if you need extra
flags or want to run it under a debugger):

```bash
cd retell_call_agent            # the project root — NOT backend/
source backend/venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8006 --reload
```

The one thing that matters here: **run this from the project root, not from
inside `backend/`.** Every internal import in this codebase is
`backend.app.xxx`, so `backend` has to be importable as a package relative
to your current directory — that only works one level up from
`backend/__init__.py`. Running the old `uvicorn app.main:app` form, or
running from inside `backend/`, will fail with a `ModuleNotFoundError`.

Verify it's up:

```bash
curl http://localhost:8006/health
# {"status":"ok","from_number_configured":true}
```

### 9.4 Running the frontend

Two different modes depending on what you're doing:

**A. Live development (hot reload — use this while working on the UI):**

```bash
cd frontend
npm run dev
```

Runs the `dev` script from `frontend/package.json`
(`vite --host 0.0.0.0 --port 8005`) — Vite's dev server on
`http://localhost:8005` with instant hot-module-reload on every save. It
reads `VITE_API_BASE_URL` from the root `.env` to know where the backend
lives (falls back to `/api` if unset) — make sure the backend is already
running first.

**B. Production-style (build once, then serve the static bundle):**

```bash
cd frontend
npm run build            # writes frontend/dist/
cd ..
./start_frontend.sh      # serves frontend/dist via uvicorn (frontend/serve.py)
```

`start_frontend.sh` does **not** run the build for you — it only serves
whatever is already sitting in `frontend/dist/`, on `FRONTEND_PORT` (default
`8005`, from the root `.env`). Use mode **A** for everyday development; only
use **B** when you specifically want to check what a real deployment will
serve.

Either way, once it's up, open `http://localhost:8005` — you should see the
dashboard with the 3 seed patients (Dave Vipul, Emiley Davis, Robert Brown).

### 9.5 Running everything via Docker

```bash
docker compose up --build
```

Builds and starts both services from the same root `.env`
(`docker-compose.yml` maps `BACKEND_PORT`/`FRONTEND_PORT`, default
`8006`/`8005`). This is the closest thing to the real deployment shape — use
it to catch environment-specific issues (missing env vars, CORS, etc.) that
running things locally might not surface.

### 9.6 Quick sanity check once both are up

1. `curl http://localhost:8006/health` → `{"status": "ok", ...}`.
2. Open the frontend URL — 3 patients should be listed, each showing **Start
   Call**.
3. Click **Start Call** on one. With real `RETELL_API_KEY` +
   `RETELL_FROM_NUMBER` configured, Retell places an actual phone call and
   the button shows "Calling…" until the call ends (6.2/6.3 above). Without
   them, the button briefly shows "Calling…" then rolls back to "Start
   Call" with an error banner — that's `_require_from_number` /
   `_execute_outbound_call` (section 4.10) failing loudly on purpose rather
   than pretending to place a call.
