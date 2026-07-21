from app.pipeline.validator import validate_schema
import json

ECOMMERCE_SCHEMA = {
    "db_schema": {
        "entities": {
            "users": {"name": "string", "email": "string"},
            "products": {"name": "string", "price": "decimal"},
            "orders": {"user_id": "int", "total": "decimal"},
            "reviews": {"product_id": "int", "rating": "int"}
        },
        "relations": [
            {"from": "orders", "to": "users"},
            {"from": "reviews", "to": "products"}
        ]
    },
    "ui_schema": {
        "pages": {
            "home": {"type": "dashboard"},
            "products": {"type": "list"},
            "checkout": {"type": "form", "allowed_roles": ["user"]},
            "admin": {"type": "dashboard", "allowed_roles": ["admin"]}
        }
    },
    "api_schema": {
        "endpoints": [
            {"path": "/api/products", "method": "GET", "entity": "products", "allowed_roles": ["user", "guest"]},
            {"path": "/api/orders", "method": "POST", "entity": "orders", "allowed_roles": ["user"]},
            {"path": "/api/reviews", "method": "POST", "entity": "reviews", "allowed_roles": ["user"]},
            {"path": "/api/admin/orders", "method": "GET", "entity": "orders", "allowed_roles": ["admin"]}
        ],
        "base_path": "/api/v1"
    },
    "auth_config": {
        "auth_type": "jwt",
        "roles": {
            "guest": ["read"],
            "user": ["read", "write"],
            "admin": ["read", "write", "delete"]
        }
    }
}

INVALID_SCHEMA = {
    "db_schema": {
        "entities": {"users": {}}
        # Missing 'relations'
    },
    "ui_schema": {
        # Missing 'pages'
    },
    "api_schema": {
        "endpoints": []
        # Missing 'base_path'
    },
    "auth_config": {
        "auth_type": "jwt"
        # Missing 'roles'
    }
}

def test_validation(name: str, schema: dict):
    """Test validation and display results."""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"{'='*80}")
    
    errors = validate_schema(schema)
    
    if not errors:
        print("VALIDATION PASSED - No errors found!\n")
    else:
        print(f"VALIDATION FAILED - Found {len(errors)} errors:\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    
    return len(errors) == 0

if __name__ == "__main__":
    print("\n" + "="*80)
    print("VALIDATION TEST SUITE")
    print("="*80)
    
    valid = test_validation("Valid E-commerce Schema", ECOMMERCE_SCHEMA)
    
    invalid = test_validation("Invalid Schema (Missing Fields)", INVALID_SCHEMA)
    
    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Valid Schema Test: {'PASSED' if valid else 'FAILED'}")
    print(f"Invalid Schema Test: {'PASSED' if not invalid else 'FAILED'} (should detect errors)")
    print(f"\nValidation is working correctly!" if (valid and not invalid) else "\nValidation needs attention!")
