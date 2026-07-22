#!/usr/bin/env python3
"""FastAPI static file server for the built frontend (frontend/dist).

Run with: uvicorn serve:app --host 0.0.0.0 --port 8005
(or `python3 serve.py [PORT]` — see start_frontend.sh / Dockerfile)
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

app = FastAPI(title="Frontend static server", docs_url=None, redoc_url=None)


def _resolve(path: str) -> Path | None:
    candidate = (DIST_DIR / path).resolve()
    if candidate.is_file() and DIST_DIR in candidate.parents:
        return candidate
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
