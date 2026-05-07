from dotenv import load_dotenv, find_dotenv
import os
from pathlib import Path

load_dotenv(find_dotenv())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes.generate import router as generate_router
from app.utils.logger import get_logger

logger = get_logger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Web Maker Bot",
        description="AI application generator: Natural Language to Executable Config",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "Retry-After",
        ],
    )

    app.include_router(generate_router)

    frontend_path = Path(__file__).parent.parent / "frontend"
    if frontend_path.exists():
        app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)