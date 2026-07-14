#!/usr/bin/env python3
"""FastAPI static file server for the built frontend (frontend/dist).

Run with: uvicorn serve:app --host 0.0.0.0 --port 8005
(or `python3 serve.py [PORT]` — see start_frontend.sh / Dockerfile)

Deployment note (see docs/DEPLOYMENT_REVERSE_PROXY.md):
The production build embeds asset URLs under the `/janus/voice-agent/`
prefix (baked in via vite's `base` config), because the public URL is
`https://ailabs.youngsoft.com/janus/voice-agent/`. Whether IT's reverse
proxy strips that prefix before forwarding to this service (port 8005) or
forwards the full path as-is isn't confirmed yet, so this server handles
both: any request path is checked with and without a leading
`janus/voice-agent/` segment before falling back to `index.html` for SPA
routing. If IT's proxy behavior turns out to need something different,
only BASE_PREFIX below should need to change.
"""
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

DIST_DIR = Path(__file__).resolve().parent / "dist"
INDEX_FILE = DIST_DIR / "index.html"

if not DIST_DIR.is_dir():
    raise RuntimeError(f"'{DIST_DIR}' not found. Run 'npm run build' first.")

# Matches vite.config.js's `base` — the path prefix baked into dist/index.html's
# asset URLs. Strip it if a request includes it, so this server works whether
# or not the upstream reverse proxy strips it first.
BASE_PREFIX = "janus/voice-agent"

app = FastAPI(title="Frontend static server", docs_url=None, redoc_url=None)


def _resolve(full_path: str) -> Path | None:
    """Map a request path to a real file under dist/, trying the path as-is
    and with BASE_PREFIX stripped. Returns None if nothing matches."""
    for candidate_path in (full_path, _strip_prefix(full_path)):
        if candidate_path is None:
            continue
        candidate = (DIST_DIR / candidate_path).resolve()
        if candidate.is_file() and DIST_DIR in candidate.parents:
            return candidate
    return None


def _strip_prefix(path: str) -> str | None:
    if path == BASE_PREFIX:
        return ""
    if path.startswith(BASE_PREFIX + "/"):
        return path[len(BASE_PREFIX) + 1 :]
    return None


@app.get("/{full_path:path}")
async def spa(full_path: str):
    path = full_path.strip("/")
    match = _resolve(path) if path else None
    if match is not None:
        headers = None
        if "assets" in match.relative_to(DIST_DIR).parts:
            headers = {"Cache-Control": "public, max-age=31536000, immutable"}
        return FileResponse(match, headers=headers)

    # No real file matched (or path was "/") — SPA fallback.
    return FileResponse(INDEX_FILE)


if __name__ == "__main__":
    import uvicorn

    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("FRONTEND_PORT", "8005"))
    uvicorn.run(app, host="0.0.0.0", port=port)
