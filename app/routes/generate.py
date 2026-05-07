from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from app.utils.logger import get_logger
from app.runtime import build_runtime_app
from app.utils.rate_limit import consume_rate_limit, get_rate_limit_status

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["generation"])

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    success: bool
    config: dict = None
    error: str = None
    metrics: dict = None

def _apply_rate_limit_headers(response: Response, rate_limit: dict) -> None:
    response.headers["X-RateLimit-Limit"] = str(rate_limit["total_limit"])
    response.headers["X-RateLimit-Remaining"] = str(rate_limit["remaining"])
    response.headers["X-RateLimit-Reset"] = str(rate_limit["reset_at"])
    response.headers["Retry-After"] = str(rate_limit["reset_after_seconds"])


@router.post("/generate", response_model=GenerateResponse)
def generate(request: Request, response: Response, data: GenerateRequest) -> GenerateResponse:
    from app.pipeline.orchestrator import Orchestrator

    rate_limit = None

    try:
        rate_limit = consume_rate_limit(request)
        _apply_rate_limit_headers(response, rate_limit)

        if not rate_limit["allowed"]:
            response.status_code = 429
            return GenerateResponse(
                success=False,
                error=f'Rate limit exceeded. You have reached the {rate_limit["total_limit"]}/day compile limit.',
                metrics={"rate_limit": rate_limit},
            )

        if not data.prompt or len(data.prompt.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Prompt must be at least 10 characters"
            )

        orchestrator = Orchestrator(max_repair_attempts=3)
        result = orchestrator.run(data.prompt)

        if not result or not isinstance(result, dict):
            return GenerateResponse(
                success=False,
                error="Failed to generate configuration - unexpected response format",
                metrics={"rate_limit": rate_limit},
            )

        if result.get("success"):
            config = result.get("config")

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
                    **result.get("metrics", {}),
                    "rate_limit": rate_limit,
                    "execution": execution_info
                }
            )

        else:
            return GenerateResponse(
                success=False,
                error=result.get("error", "Generation failed"),
                metrics={
                    **result.get("metrics", {}),
                    "rate_limit": rate_limit,
                },
            )

    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        return GenerateResponse(
            success=False,
            error=str(e),
            metrics={"error_type": type(e).__name__, "rate_limit": rate_limit}
        )

@router.get("/health")
def health():
    return {"status": "healthy"}


@router.get("/rate-limit")
def rate_limit_status(request: Request):
    return {"rate_limit": get_rate_limit_status(request)}