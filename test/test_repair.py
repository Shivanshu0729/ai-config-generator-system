from app.pipeline.repair import repair_schema

def test_repair():
    schema = {}
    errors = ["Missing UI"]
    new_schema = repair_schema(schema, errors)
    assert "ui" in new_schema