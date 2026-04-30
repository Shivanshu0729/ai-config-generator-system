from app.pipeline.validator import validate_schema

def test_invalid_schema():
    schema = {}
    errors = validate_schema(schema)
    assert len(errors) > 0