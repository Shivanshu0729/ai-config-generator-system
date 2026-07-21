import os
import pytest
from app.pipeline.repair import repair_schema


@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set"
)
def test_repair():
    """Test that the repair engine can fix validation errors."""
    schema = {
        "db_schema": {},
        "ui_schema": {},
        "api_schema": {},
        "auth_config": {}
    }
    errors = [
        "DB schema missing 'entities'",
        "UI schema missing 'pages'"
    ]
    new_schema = repair_schema(schema, errors)
    
    # Check that missing fields were added
    assert "entities" in new_schema["db_schema"]
    assert "pages" in new_schema["ui_schema"]
    assert isinstance(new_schema["db_schema"]["entities"], dict)
    assert isinstance(new_schema["ui_schema"]["pages"], dict)