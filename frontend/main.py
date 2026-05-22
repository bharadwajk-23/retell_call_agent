from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
import uvicorn

app = FastAPI()
FRONTEND_DIR = Path(__file__).resolve().parent

# Serve entire frontend folder
app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="static"
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )