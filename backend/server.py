from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
import sys

# Add parent dir to path to find backend module if running from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.typewriter import session

app = FastAPI()

class TypingRequest(BaseModel):
    url: str
    text: str
    wpm: int = 60
    cleanup: bool = False

@app.post("/api/start")
async def start_typing(request: TypingRequest, background_tasks: BackgroundTasks):
    if session.is_running:
        return {"status": "error", "message": "Already running"}
    
    # Run the typing task in background
    background_tasks.add_task(session.type_content, request.url, request.text, request.wpm)
    return {"status": "started"}

@app.post("/api/stop")
async def stop_typing():
    session.stop_requested = True
    await session.close_browser()
    return {"status": "stopping"}

@app.get("/api/status")
async def get_status():
    return {
        "status": session.status,
        "progress": session.progress,
        "is_running": session.is_running
    }

@app.post("/api/login")
async def login():
    """Launches browser for login only."""
    success, message = await session.launch_browser(login_mode=True)
    if success:
        return {"status": "Login browser launched. Close it when done."}
    else:
        return {"status": f"Error launching browser: {message}"}

# Serve Frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
