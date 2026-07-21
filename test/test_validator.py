from app.pipeline.validator import validate_schema

def test_invalid_schema():
    """Test that empty schemas produce validation errors."""
    schema = {}
    errors = validate_schema(schema)
    assert len(errors) > 0
    assert any("missing" in error.lower() for error in errors)


def test_valid_schema():
    """Test that properly structured schemas pass validation."""
    schema = {
        "db_schema": {
            "entities": {"users": {"name": "string"}},
            "relations": []
        },
        "ui_schema": {
            "pages": {"home": {"type": "dashboard"}}
        },
        "api_schema": {
            "endpoints": [{"entity": "users", "method": "GET"}],
            "base_path": "/api/v1"
        },
        "auth_config": {
            "auth_type": "jwt",
            "roles": {"user": {}, "admin": {}}
        }
    }
    errors = validate_schema(schema)
    assert len(errors) == 0, f"Expected no errors, got: {errors}"