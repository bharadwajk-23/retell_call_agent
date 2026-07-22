# AI Physiotherapy Call Agent

An AI voice-calling system for a physiotherapy clinic. Staff open a
dashboard, see patients who missed prescribed exercises, and start an
outbound AI phone call (via [Retell AI](https://www.retellai.com)) that
checks provider availability and books a follow-up appointment — no human
on the line required.

The project is split into two fully independent services:

- **`backend/`** — FastAPI REST API (Python). Owns all business logic and
  in-memory data. Never serves any frontend assets.
- **`frontend/`** — React + Vite single-page app. Talks to the backend only
  over HTTP, via `VITE_API_BASE_URL`.

They run on separate ports, can be deployed independently, and communicate
exclusively through the REST API described below.

## Architecture

```
┌────────────────────┐   REST (fetch)   ┌───────────────────────┐        ┌────────────┐
│  React SPA          │ ───────────────▶ │  FastAPI backend       │──────▶ │  Retell AI  │
│  localhost:8005      │ ◀─────────────── │  localhost:8006        │        │  voice agent│
└────────────────────┘   JSON responses  └──────────┬────────────┘        └─────┬──────┘
                                                       ▲                          │ places call
                                    Custom Functions / │                          ▼
                                    Webhook callbacks  │                    ┌───────────┐
                                                        └────────────────── │  Patient   │
                                                                            └───────────┘
```

During a call, Retell calls back into the backend as "Custom Functions"
(`/providers/availability`, `/appointments/book`) and sends call
lifecycle events to `/webhooks/retell`. See
[`docs/RETELL_SETUP.md`](docs/RETELL_SETUP.md) for the full dashboard
configuration.

## Project structure

```
retell_call_agent/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app factory, middleware, lifespan
│   │   ├── config/             # Settings (env vars) + path helpers
│   │   ├── routers/            # HTTP layer only — no business logic
│   │   ├── services/           # Business logic (calls, patients, appointments, providers, webhooks)
│   │   ├── repositories/       # In-memory data access (patients, appointments, calls, logs)
│   │   ├── models/              # Domain dataclasses
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── middleware/          # Centralized error handling + request logging
│   │   ├── utils/                # Logging, phone normalization, JSON helpers
│   │   └── data/provider_details.json
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/Dashboard/     # The one page in the app today
│   │   ├── components/           # Navbar, PatientTable, CallActionButton, etc.
│   │   ├── context/               # PatientsContext — avoids prop drilling
│   │   ├── hooks/                 # usePatients (context consumer), usePatientsData, useTimeOfDay
│   │   ├── services/api/          # All fetch() calls live here, nowhere else
│   │   ├── constants/              # POLL_INTERVAL_MS, thresholds, status enum
│   │   └── utils/
│   ├── package.json
│   ├── serve.py            # FastAPI/uvicorn static server for dist/ (SPA fallback)
│   ├── requirements.txt
│   └── Dockerfile
├── docs/
│   └── RETELL_SETUP.md          # Retell dashboard configuration (agent prompt, custom functions, webhook)
├── initialize.sh                # installs backend + frontend dependencies
├── start_backend.sh             # runs the FastAPI backend
├── start_frontend.sh            # builds + serves the frontend
├── docker-compose.yml
├── .env.example                 # single env file for the whole project
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- A [Retell AI](https://www.retellai.com) account with a phone number
  imported (Telnyx/Twilio underneath — configured in Retell's dashboard,
  not in this repo)
- Docker + Docker Compose (optional, for containerized deployment)

## Environment variables

Every setting is read from the environment — nothing is hardcoded. There is
a single `.env` at the project root (copy from `.env.example`); the backend
(via `pydantic-settings`), the frontend build (via Vite's `envDir`), and
`docker-compose.yml` all read from that one file — there's no per-service
`.env`.

| Variable | Default | Purpose |
|---|---|---|
| `HOST` / `PORT` | `0.0.0.0` / `8006` | Bind address for uvicorn |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `CORS_ORIGINS` | `http://localhost:8005` | Comma-separated list of allowed frontend origins — no wildcard |
| `RETELL_API_KEY` | *(none)* | Retell API key — required for real calls |
| `RETELL_AGENT_ID` | *(none)* | Agent used for `override_agent_id` |
| `RETELL_FROM_NUMBER` | *(none)* | Telnyx/Twilio number provisioned in Retell (E.164) |
| `PROVIDER_DETAILS_PATH` | `app/data/provider_details.json` | Override provider availability reference data path |
| `VITE_API_BASE_URL` | `http://localhost:8006` | Backend URL baked into the frontend at build time (Vite only exposes `VITE_`-prefixed vars, and only at build time — rebuild if this changes). No `/api` suffix — backend routes are unprefixed. |
| `FRONTEND_PORT` | `8005` | Port the built frontend is served on (`start_frontend.sh` / docker-compose) |
| `BACKEND_PORT` | `8006` | docker-compose only: host-side port mapping for the backend container |

## Running locally (without Docker)

```bash
cp .env.example .env   # fill in your Retell credentials
./initialize.sh        # creates backend/venv + frontend/venv, installs backend & frontend deps
./start_backend.sh     # http://localhost:8006 (docs at /docs), served by uvicorn
```

For the frontend, pick one:

- **Day-to-day development (hot reload):**
  ```bash
  cd frontend && npm run dev   # http://localhost:8005, instant reload on save
  ```
- **Production-style (build once, serve the static bundle):**
  ```bash
  cd frontend && npm run build   # writes frontend/dist/
  cd .. && ./start_frontend.sh   # serves frontend/dist on http://localhost:8005 via uvicorn
  ```
  `start_frontend.sh` does **not** run the build for you — it only serves
  whatever is already in `dist/`, so run `npm run build` first (or whenever
  frontend code changes and you want to check the built output).

Run the backend and frontend commands in separate terminals (or under a
process manager / systemd). Both read their configuration from the single
root `.env`.

## Running with Docker Compose

```bash
cp .env.example .env   # fill in Retell credentials
docker compose up --build
```

- Frontend: `http://localhost:8005`
- Backend: `http://localhost:8006` (health check at `/health`, readiness at `/ready`)

## API reference

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe (checks Retell config) |
| GET | `/patients` | List patients |
| POST | `/patients/reset` | Reset demo data (`patient_id` query param optional) |
| POST | `/calls/start` | Start outbound call by `patient_id` (dashboard action) |
| POST | `/calls/make` | Start outbound call by `phone` |
| GET | `/calls/status?phone=...` | Current status of the last call for a phone number |
| GET | `/calls/transcripts` | All logged call/webhook events |
| GET | `/providers/availability?provider_name=...` | Free slots for a provider (Retell custom function) |
| POST | `/appointments` | Create an appointment (generic) |
| POST | `/appointments/book` | Book an appointment (Retell custom function) |
| GET | `/appointments` | List booked appointments |
| POST | `/webhooks/retell` | Retell call-lifecycle/transcript webhook |

Full interactive docs: `http://localhost:8006/docs` (Swagger) or `/redoc`.

Configuring the Retell dashboard's Custom Function and webhook URLs against
these paths is covered in [`docs/RETELL_SETUP.md`](docs/RETELL_SETUP.md).

## Data & persistence

Patients, active calls, appointments, and call logs live in memory in the
backend process (matching the original app's behavior) — restarting the
backend resets them. Provider availability is the only data read from disk
(`backend/app/data/provider_details.json`). There is no database; swapping
one in only requires reimplementing the classes in `backend/app/repositories/`.

## Logging & error handling

- Structured logging (Python `logging`, not `print()`) for every request,
  call event, and booking event — see `backend/app/core/logging.py`.
- Centralized exception handlers return consistent `{"detail": ...}` JSON
  and never leak stack traces (`backend/app/middleware/error_handlers.py`).
- The Retell webhook endpoint additionally guards itself so a malformed
  payload from Retell always gets a logged, explicit response.

## What changed in this refactor

This app was previously a single FastAPI service that also built and
served the React app's static files (routes lived at `/patients`,
`/start-call`, `/providers/availability`, etc., with two competing
`main.py`/`main_new.py` implementations). It has been split into two
independently runnable services with a layered backend architecture and
environment-driven configuration (no hardcoded secrets). Application
behavior — the dashboard, Start Call, Reset, Retell calling, availability,
booking, webhooks, transcripts, and 2-second polling — is unchanged.

## License

Demonstration use only.
