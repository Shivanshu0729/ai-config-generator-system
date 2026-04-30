"""Schema generation stage - create concrete DB/UI/API schemas."""

import json
from app.services.llm_service import LLMService
from app.models.schema_models import GeneratedConfig, DBSchema, Entity, SchemaField, FieldType, UISchema, UIPage, UIComponent, APISchema, APIEndpoint, HTTPMethod, AuthConfig, AuthRole
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SchemaGenerator:
    """Generate concrete schemas from design."""
    
    def __init__(self):
        self.llm = LLMService()
    
    def generate(self, intent: dict, design: dict) -> dict:
        """Generate concrete schemas from design."""
        db_schema = self._generate_db_schema(intent, design)
        
        ui_schema = self._generate_ui_schema(intent, design)
        
        api_schema = self._generate_api_schema(intent, design, db_schema)
        
        auth_config = self._generate_auth_config(intent)
        
        return {
            "db_schema": db_schema,
            "ui_schema": ui_schema,
            "api_schema": api_schema,
            "auth_config": auth_config,
        }
    
    def _generate_db_schema(self, intent: dict, design: dict) -> dict:
        """Generate database schema."""
        system_prompt = """You are a database schema designer.
        
Generate a detailed database schema with:
1. Each entity as a table
2. All necessary fields with types (string, integer, boolean, email, date, datetime, phone, json)
3. Foreign keys for relationships
4. Appropriate indexes

Return ONLY valid JSON."""
        
        entities_str = ", ".join(intent.get("entities", []))
        prompt = f"""Design database schema for:
Entities: {entities_str}

From design:
Relationships: {json.dumps(design.get('relationships', []))}
Access rules: {json.dumps(design.get('access_rules', {}))}

Create complete schema with all entities, fields (include created_at, updated_at timestamps), and relationships."""
        
        schema_desc = """{{
  "entities": {{
    "EntityName": {{
      "fields": {{
        "field_name": {{"type": "string", "required": true, "indexed": false}}
      }}
    }}
  }},
  "relations": [{{"from": "Entity1", "to": "Entity2", "type": "one_to_many"}}]
}}"""
        
        try:
            schema = self.llm.generate_json(
                prompt=prompt,
                system=system_prompt,
                schema_description=schema_desc,
                temperature=0.5  # Lower temp for consistency
            )
            logger.info(f"DB schema generated: {len(schema.get('entities', {}))} entities")
            return schema
        
        except Exception as e:
            logger.error(f"DB schema generation failed: {e}")
            return {"entities": {}, "relations": []}
    
    def _generate_ui_schema(self, intent: dict, design: dict) -> dict:
        """Generate UI schema."""
        pages_list = json.dumps(design.get("pages", []), indent=2)
        
        system_prompt = """You are a UI/UX designer.
        
Generate UI schema with:
1. Pages with routes and titles
2. Components on each page (input, button, table, form, etc.)
3. Field bindings to data
4. Auth requirements per page

Return ONLY valid JSON."""
        
        prompt = f"""Create UI schema for pages:
{pages_list}

Roles: {', '.join(intent.get('roles', []))}

For each page:
- Assign a route path
- List UI components needed
- Bind components to data fields
- Mark auth requirements and role access"""
        
        schema_desc = """{{
  "pages": {{
    "page_name": {{
      "route": "/path",
      "title": "Page Title",
      "components": [{{"type": "input", "id": "field-name"}}],
      "auth_required": true,
      "allowed_roles": ["user"]
    }}
  }}
}}"""
        
        try:
            schema = self.llm.generate_json(
                prompt=prompt,
                system=system_prompt,
                schema_description=schema_desc,
                temperature=0.5
            )
            logger.info(f"UI schema generated: {len(schema.get('pages', {}))} pages")
            return schema
        
        except Exception as e:
            logger.error(f"UI schema generation failed: {e}")
            return {"pages": {}}
    
    def _generate_api_schema(self, intent: dict, design: dict, db_schema: dict) -> dict:
        """Generate API schema."""
        system_prompt = """You are an API designer.
        
Design RESTful API endpoints:
1. CRUD operations for each entity
2. Custom endpoints for features
3. Auth requirements
4. Request/response bodies

Return ONLY valid JSON."""
        
        entities = json.dumps(list(db_schema.get("entities", {}).keys()))
        features = ", ".join(intent.get("features", []))
        
        prompt = f"""Design API for:
Entities: {entities}
Features: {features}
Roles: {', '.join(intent.get('roles', []))}

Generate endpoints for:
1. Standard CRUD for each entity
2. Custom endpoints for each feature
3. Include auth headers for role-based access"""
        
        schema_desc = """{{
  "endpoints": [{{
    "path": "/api/v1/entities",
    "method": "GET",
    "name": "list_entities",
    "auth_required": true,
    "allowed_roles": ["user"],
    "response_body": {{}}
  }}],
  "base_path": "/api/v1"
}}"""
        
        try:
            schema = self.llm.generate_json(
                prompt=prompt,
                system=system_prompt,
                schema_description=schema_desc,
                temperature=0.5
            )
            logger.info(f"API schema generated: {len(schema.get('endpoints', []))} endpoints")
            return schema
        
        except Exception as e:
            logger.error(f"API schema generation failed: {e}")
            return {"endpoints": [], "base_path": "/api/v1"}
    
    def _generate_auth_config(self, intent: dict) -> dict:
        """Generate auth configuration."""
        roles = intent.get("roles", ["user"])
        premium_features = intent.get("premium_features", [])
        
        auth_type = "jwt"  
        
        role_permissions = {}
        for role in roles:
            if role == "admin":
                role_permissions[role] = ["read", "write", "delete", "manage_users"]
            elif role == "premium_user":
                role_permissions[role] = ["read", "write", "access_premium"]
            else:
                role_permissions[role] = ["read", "write"]
        
        return {
            "auth_type": auth_type,
            "roles": role_permissions,
            "premium_features": premium_features,
        }