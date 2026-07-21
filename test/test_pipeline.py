import os
import pytest
from app.pipeline.orchestrator import run_pipeline


@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set"
)
def test_basic_prompt():
    """Test that the pipeline can process a basic prompt."""
    result = run_pipeline("build crm with login")
    assert result is not None
    assert "success" in result
    # Success depends on LLM availability, so just check structure
    assert "config" in result or "error" in result
    assert "metrics" in result