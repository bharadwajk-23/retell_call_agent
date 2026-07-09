# Quick Reference: Reverse Proxy Deployment

## 5-Minute Summary

**Deployment Path:** `/janus/voice-agent/`

### Frontend Changes ✅

```javascript
// vite.config.js
base: '/janus/voice-agent/',
```

```bash
# .env (production)
VITE_API_BASE_URL=/janus/voice-agent/api
```

### Backend Changes ✅

```python
# app/main.py
app = FastAPI(
    root_path="/janus/voice-agent",
)

# Add TrustedHostMiddleware first
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(CORSMiddleware, ...)
```

```python
# app/config/settings.py
CORS_ORIGINS: str = "https://ailabs.youngsoft.com"
```

---

## URL Mapping

| Type | Public URL | Internal |
|------|-----------|----------|
| Frontend HTML | `https://ailabs.youngsoft.com/janus/voice-agent/` | Frontend:8005 |
| Frontend Assets | `https://ailabs.youngsoft.com/janus/voice-agent/assets/...` | Frontend:8005 |
| Backend API | `https://ailabs.youngsoft.com/janus/voice-agent/api/calls/start` | Backend:8006 → `/api/calls/start` |
| Swagger Docs | `https://ailabs.youngsoft.com/janus/voice-agent/docs` | Backend:8006 |

---

## How It Works

```
Browser
  ↓
Request: https://ailabs.youngsoft.com/janus/voice-agent/api/patients
  ↓
Reverse Proxy
  ↓
Matches: /janus/voice-agent/api/*
  ↓
Routes to: backend:8006
  ↓
Strips prefix: /janus/voice-agent
  ↓
FastAPI receives: POST /api/patients (with root_path="/janus/voice-agent")
  ↓
Response sent back through reverse proxy
```

---

## Critical Config Values

| Component | Setting | Value |
|-----------|---------|-------|
| Frontend | Vite base | `/janus/voice-agent/` |
| Frontend | API URL | `/janus/voice-agent/api` |
| Backend | root_path | `/janus/voice-agent` |
| Backend | CORS Origins | `https://ailabs.youngsoft.com` |
| Backend | TrustedHostMiddleware | Enabled ✓ |

---

## Verification Commands

```bash
# Test 1: Frontend page loads
curl -I https://ailabs.youngsoft.com/janus/voice-agent/
→ HTTP 200 with index.html

# Test 2: Assets load
curl -I https://ailabs.youngsoft.com/janus/voice-agent/assets/main.js
→ HTTP 200

# Test 3: Backend health check
curl https://ailabs.youngsoft.com/janus/voice-agent/api/health
→ {"status": "ok"}

# Test 4: Swagger available
curl -I https://ailabs.youngsoft.com/janus/voice-agent/docs
→ HTTP 200

# Test 5: Frontend API call (browser Network tab)
fetch("/janus/voice-agent/api/patients")
→ Should succeed, not show CORS errors or 404
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Assets 404 | Vite base not set | Add `base: "/janus/voice-agent/"` to vite.config.js |
| Page not found | SPA routing issue | Reverse proxy must serve index.html for unknown paths |
| API CORS error | CORS_ORIGINS wrong | Update .env: `CORS_ORIGINS=https://ailabs.youngsoft.com` |
| API 404 | API URL wrong | Use relative path: `/janus/voice-agent/api` |
| Swagger 404 | root_path not set | Add `root_path="/janus/voice-agent"` to FastAPI |

---

## Files Modified

✅ `frontend/vite.config.js` - Added base path  
✅ `.env.example` - Updated API URL  
✅ `backend/app/main.py` - Added root_path & TrustedHostMiddleware  
✅ `backend/app/config/settings.py` - Updated CORS origins  

**Documentation:**  
📄 `docs/DEPLOYMENT_REVERSE_PROXY.md` - Full guide
