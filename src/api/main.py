"""
FastAPI Server Entry Point for PS02 SOC Dashboard.
Serves both REST API endpoints and static compiled React assets.
"""

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes.api_routes import router as api_router

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DIST_DIR = BASE_DIR / "frontend" / "dist"

app = FastAPI(
    title="PS02 Offline Security Incident Triage Assistant",
    description="Air-Gapped Small Language Model SOC Assistant API",
    version="2.0.0"
)

# CORS middleware for local development with Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes first
app.include_router(api_router)


# If compiled React frontend dist exists, mount and serve static files
if DIST_DIR.exists() and (DIST_DIR / "index.html").exists():
    # Mount assets folder
    assets_dir = DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # SPA Fallback for client-side routing
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # Do not catch /api routes
        if full_path.startswith("api/"):
            return None
        file_path = DIST_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(DIST_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=False)
