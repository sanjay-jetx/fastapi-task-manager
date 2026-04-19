from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os

from app.database import Base, engine
from app.routes import auth
from app.routes import tasks

app = FastAPI(title="Task Manager API")

# Create tables
Base.metadata.create_all(bind=engine)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; in production restrict to actual frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["auth"])
app.include_router(tasks.router, tags=["tasks"])

# Redirect root to /frontend/index.html
@app.get("/")
def home():
    return RedirectResponse(url="/frontend/index.html")

# Mount frontend directory for static file serving
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")
else:
    print(f"Warning: Frontend directory not found at {frontend_path}")