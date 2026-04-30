from app.pipeline.orchestrator import run_pipeline

def test_basic_prompt():
    result = run_pipeline("build crm with login")
    assert "final_schema" in result