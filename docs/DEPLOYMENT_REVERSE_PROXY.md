# Deployment Behind Reverse Proxy Path Prefix

## Overview

This application is designed to run behind a reverse proxy that serves it at a path prefix: `/janus/voice-agent/`

**Public URLs:**
- Frontend: `https://ailabs.youngsoft.com/janus/voice-agent/`
- Backend API: `https://ailabs.youngsoft.com/janus/voice-agent/api/*`

**Internal Services (behind proxy):**
- Frontend: Port 8005
- Backend: Port 8006

**Reverse Proxy Routing:**
```
https://ailabs.youngsoft.com/janus/voice-agent/*        → Frontend (port 8005)
https://ailabs.youngsoft.com/janus/voice-agent/api/*    → Backend (port 8006)
```

---

## Architecture & Data Flow

### Request Flow

```
Client Browser
      ↓
Reverse Proxy (nginx/apache)
      ├─ /janus/voice-agent/*      → Frontend (port 8005, serves HTML/JS)
      └─ /janus/voice-agent/api/*  → Backend (port 8006, FastAPI)
                                          ↓
                                    Removes /janus/voice-agent prefix
                                          ↓
                                    /api/patients
                                    /api/calls/start
                                    etc.
```

### Frontend to Backend Communication

```
Frontend JavaScript                Backend FastAPI
┌─────────────────────┐            ┌────────────────────┐
│ fetch("/janus/voice-│            │ @app.post("/api/   │
│  agent/api/calls/   │─ HTTP ────→│  calls/start")     │
│  start")            │            │                    │
│                     │            │ (receives request  │
│                     │            │  without prefix)   │
│                     │← JSON ─────│                    │
└─────────────────────┘            └────────────────────┘
```

---

## Required Changes

### 1. Frontend: Vite Base Path

**File:** `frontend/vite.config.js`

**Change:** Add `base: "/janus/voice-agent/"`

```javascript
export default defineConfig({
  plugins: [react()],
  envDir: fileURLToPath(new URL('..', import.meta.url)),
  base: '/janus/voice-agent/',  // ← Add this line
  // ... rest of config
})
```

**Why:** Vite needs to know the public path where the app is deployed so it can:
- Correctly reference static assets (`/janus/voice-agent/assets/...`)
- Set up correct module imports
- Handle client-side routing if added later

**Impact:** Without this, assets return 404 because the browser requests `/assets/main.js` instead of `/janus/voice-agent/assets/main.js`

---

### 2. Frontend: Environment Variable

**File:** `.env.example` (and actual `.env` when deployed)

**Change:** Update `VITE_API_BASE_URL` to use relative path

```bash
# Before:
VITE_API_BASE_URL=http://localhost:8006/api

# After:
VITE_API_BASE_URL=/janus/voice-agent/api
```

**Why:** 
- Hardcoding `http://localhost:8006` only works locally
- In production, the internal port 8006 is not accessible from the browser
- A relative path `/janus/voice-agent/api` works through the reverse proxy
- The browser sends requests to the same origin/path, and the reverse proxy routes them correctly

**How it works:**
```
Browser → fetch("/janus/voice-agent/api/calls/start")
          ↓
    Reverse Proxy sees /janus/voice-agent/api/*
          ↓
    Strips /janus/voice-agent prefix
          ↓
    Routes to backend: http://backend:8006/api/calls/start
```

**Frontend API Client (src/services/api/client.js):**
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    // API_BASE_URL = "/janus/voice-agent/api"
    // path = "/calls/start"
    // Result: "/janus/voice-agent/api/calls/start"
    ...
  })
}
```

---

### 3. Backend: FastAPI Root Path

**File:** `backend/app/main.py`

**Change:** Add `root_path="/janus/voice-agent"` to FastAPI initialization

```python
def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="AI Physiotherapy Call Agent API",
        version="2.0.0",
        lifespan=lifespan,
        root_path="/janus/voice-agent",  # ← Add this line
    )
    # ...
```

**Why:**
- FastAPI uses `root_path` to understand the deployment context when behind a proxy
- Enables correct generation of OpenAPI/Swagger documentation URLs
- Tells FastAPI that it's deployed at `/janus/voice-agent` prefix
- Important for ASGI spec compliance and reverse proxy detection

**Impact:**
- Swagger UI accessible at `https://ailabs.youngsoft.com/janus/voice-agent/docs`
- ReDoc accessible at `https://ailabs.youngsoft.com/janus/voice-agent/redoc`
- Proper X-Forwarded-* header handling

---

### 4. Backend: Trusted Host Middleware

**File:** `backend/app/main.py`

**Change:** Add `TrustedHostMiddleware` (must be added first, before CORS)

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

def create_app() -> FastAPI:
    # ... FastAPI initialization ...

    # Trusted host middleware must be added FIRST (outermost) 
    # so it processes before other middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # Will validate against X-Forwarded-Host if present
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # ...
```

**Why:**
- Reverse proxies send `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-For` headers
- FastAPI needs to trust these headers to correctly identify the client and protocol
- Middleware order matters: TrustedHostMiddleware should be added first (outermost)
- CORS depends on correct host detection

**How it works:**
```
Request from reverse proxy includes:
  X-Forwarded-Host: ailabs.youngsoft.com
  X-Forwarded-Proto: https
  X-Forwarded-For: <client-ip>

TrustedHostMiddleware validates these headers
CORS middleware uses corrected request information
```

---

### 5. Backend: CORS Configuration

**File:** `backend/app/config/settings.py`

**Change:** Update `CORS_ORIGINS` to include production domain

```python
class Settings(BaseSettings):
    # --- CORS ---
    # Comma-separated list of allowed origins (frontend URLs)
    # Production: https://ailabs.youngsoft.com (reverse proxy frontend)
    # Development: http://localhost:5173
    # Use both in development/staging: "http://localhost:5173,https://ailabs.youngsoft.com"
    CORS_ORIGINS: str = "http://localhost:5173,https://ailabs.youngsoft.com"
```

**Why:**
- Browser CORS policy requires the backend to explicitly allow requests from the frontend origin
- In production, the frontend origin is `https://ailabs.youngsoft.com` (not `http://localhost:8006`)
- The backend needs to list all allowed origins that will make requests to it

**Environment Variable:**
```bash
# .env for production
CORS_ORIGINS=https://ailabs.youngsoft.com

# .env for development (allows both local and production)
CORS_ORIGINS=http://localhost:5173,https://ailabs.youngsoft.com
```

---

## Deployment Checklist

### Before Deploying

- [ ] Verify `frontend/vite.config.js` has `base: "/janus/voice-agent/"`
- [ ] Verify `.env` (production) has `VITE_API_BASE_URL=/janus/voice-agent/api`
- [ ] Verify `.env` (production) has `CORS_ORIGINS=https://ailabs.youngsoft.com` (or your domain)
- [ ] Verify `backend/app/main.py` has `root_path="/janus/voice-agent"`
- [ ] Verify `TrustedHostMiddleware` is added to FastAPI

### Frontend Build

```bash
# Build the frontend
npm run build

# Verify dist/ folder contains index.html and assets/
ls dist/
ls dist/assets/
```

**Expected output structure:**
```
dist/
  index.html
  assets/
    main.js
    main.css
    [other files]
```

### Backend Startup

```bash
# Verify backend starts without errors
python -m uvicorn app.main:app --host 0.0.0.0 --port 8006

# Should see:
# INFO: Uvicorn running on http://0.0.0.0:8006
# INFO: Starting AI Physiotherapy Call Agent API (env=production, mock_calls=false)
```

### Reverse Proxy Configuration

Ensure the reverse proxy is configured correctly:

```nginx
# Example nginx configuration
upstream frontend {
    server 127.0.0.1:8005;
}

upstream backend {
    server 127.0.0.1:8006;
}

server {
    listen 80;
    server_name ailabs.youngsoft.com;

    # Frontend: /janus/voice-agent/* → port 8005
    location /janus/voice-agent/ {
        proxy_pass http://frontend/;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Backend API: /janus/voice-agent/api/* → port 8006
    location /janus/voice-agent/api/ {
        proxy_pass http://backend/api/;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Important:** Ensure reverse proxy sets `X-Forwarded-*` headers. FastAPI and frontend both depend on these.

---

## Testing the Deployment

### Test 1: Frontend loads correctly

```bash
curl -I https://ailabs.youngsoft.com/janus/voice-agent/
# Expected: HTTP 200
# Should return index.html
```

### Test 2: Static assets load

```bash
curl -I https://ailabs.youngsoft.com/janus/voice-agent/assets/main.js
# Expected: HTTP 200 (or 206 partial content)
```

### Test 3: Backend API responds

```bash
curl https://ailabs.youngsoft.com/janus/voice-agent/api/health
# Expected: {"status": "ok"}
```

### Test 4: Swagger UI works

Navigate to: `https://ailabs.youngsoft.com/janus/voice-agent/docs`

Should see Swagger UI with all endpoints listed under `/api/` prefix.

### Test 5: Frontend can call backend

1. Open browser dev tools (F12)
2. Go to `https://ailabs.youngsoft.com/janus/voice-agent/`
3. Open Network tab
4. Interact with the app (e.g., load patients)
5. Verify network requests go to `https://ailabs.youngsoft.com/janus/voice-agent/api/*`
6. Should NOT see requests to `http://localhost:8006` or `/api/*` (without prefix)

---

## Troubleshooting

### Problem: "Not Found" when opening the frontend

**Cause:** Nginx not configured to serve index.html for the SPA
**Solution:** Ensure reverse proxy has `try_files $uri $uri/ /janus/voice-agent/index.html;`

### Problem: Static assets return 404

**Cause:** Vite base path not set, or reverse proxy not routing /assets/ correctly
**Solution:** 
- Check `frontend/vite.config.js` has `base: "/janus/voice-agent/"`
- Rebuild frontend: `npm run build`

### Problem: API calls fail with CORS error

**Cause:** Backend CORS_ORIGINS doesn't include the frontend origin
**Solution:**
- Check `.env` has `CORS_ORIGINS=https://ailabs.youngsoft.com`
- Check browser console for actual CORS error message

### Problem: API calls fail with "connection refused"

**Cause:** Frontend using absolute URL (e.g., `http://localhost:8006/api`) instead of relative path
**Solution:**
- Check `.env` has `VITE_API_BASE_URL=/janus/voice-agent/api` (not `http://localhost:8006/api`)
- Rebuild and redeploy frontend

### Problem: Swagger UI returns 404

**Cause:** FastAPI doesn't know about root_path, generates wrong URLs
**Solution:** Check `backend/app/main.py` has `root_path="/janus/voice-agent"`

---

## Local Development

For local development without the reverse proxy prefix, use:

```bash
# .env (local)
ENV=development
VITE_API_BASE_URL=http://localhost:8006/api
CORS_ORIGINS=http://localhost:5173
```

Frontend runs on `http://localhost:5173` and directly communicates with backend on `http://localhost:8006`.

For production:

```bash
# .env (production)
ENV=production
VITE_API_BASE_URL=/janus/voice-agent/api
CORS_ORIGINS=https://ailabs.youngsoft.com
```

Frontend is served at `https://ailabs.youngsoft.com/janus/voice-agent/` through the reverse proxy.

---

## Summary of Changes

| File | Change | Why |
|------|--------|-----|
| `frontend/vite.config.js` | Add `base: "/janus/voice-agent/"` | Assets must load from correct path |
| `.env` | `VITE_API_BASE_URL=/janus/voice-agent/api` | API calls must use reverse proxy path |
| `backend/app/main.py` | Add `root_path="/janus/voice-agent"` | FastAPI needs to know deployment prefix |
| `backend/app/main.py` | Add `TrustedHostMiddleware` | Process X-Forwarded-* headers from proxy |
| `backend/app/config/settings.py` | Update `CORS_ORIGINS` to include production domain | Allow cross-origin requests from frontend |

All changes work together to ensure the frontend and backend communicate correctly through the reverse proxy at `/janus/voice-agent/`.
