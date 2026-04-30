from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.pipeline.orchestrator import Orchestrator
from app.utils.logger import get_logger
from app.runtime import build_runtime_app  

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["generation"])

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    success: bool
    config: dict = None
    error: str = None
    metrics: dict = None

@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    if not request.prompt or len(request.prompt.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Prompt must be at least 10 characters"
        )

    try:
        orchestrator = Orchestrator(max_repair_attempts=3)
        result = orchestrator.run(request.prompt)

        if result["success"]:
            config = result["config"]

            try:
                runtime_app = build_runtime_app(config)

                execution_info = {
                    "status": "success",
                    "message": "Runtime app successfully created",
                    "total_endpoints": len(
                        config.get("api_schema", {}).get("endpoints", [])
                    )
                }

            except Exception as runtime_error:
                execution_info = {
                    "status": "failed",
                    "error": str(runtime_error)
                }

            return GenerateResponse(
                success=True,
                config=config,
                metrics={
                    **result["metrics"],
                    "execution": execution_info   
                }
            )

        else:
            return GenerateResponse(
                success=False,
                error=result["error"],
                metrics=result["metrics"]
            )

    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health():
    return {"status": "healthy"}