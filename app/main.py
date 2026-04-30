from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.generate import router as generate_router
from app.utils.logger import get_logger

logger = get_logger(__name__)

load_dotenv()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
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
    )
    
    app.include_router(generate_router)
    
    @app.get("/")
    def root():
        return {
            "name": "Web Maker Bot",
            "version": "1.0.0",
            "docs": "/docs",
            "description": "Generate complete application configs from natural language"
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)