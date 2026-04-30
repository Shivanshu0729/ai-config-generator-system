"""Repair engine - intelligently fix validation errors."""

import json
from app.services.llm_service import LLMService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RepairEngine:
    """Intelligently repair validation errors."""
    
    def __init__(self):
        self.llm = LLMService()
    
    def repair(self, errors: list[str], db_schema: dict, ui_schema: dict, api_schema: dict, auth_config: dict, intent: dict = None) -> tuple[dict, dict, dict, dict]:
        """Repair schemas based on validation errors."""
        if not errors:
            return db_schema, ui_schema, api_schema, auth_config
        
        logger.info(f"Repairing {len(errors)} validation errors...")
        
        missing_fields = [e for e in errors if "missing" in e.lower()]
        consistency_errors = [e for e in errors if "unknown" in e.lower() or "references" in e.lower()]
        logic_errors = [e for e in errors if "no" in e.lower()]
        
        if missing_fields:
            db_schema, ui_schema, api_schema, auth_config = self._fix_missing_fields(
                missing_fields, db_schema, ui_schema, api_schema, auth_config
            )
        
        if consistency_errors:
            db_schema, ui_schema, api_schema = self._fix_consistency_issues(
                consistency_errors, db_schema, ui_schema, api_schema
            )
        
        if logic_errors:
            api_schema = self._fix_logic_issues(
                logic_errors, db_schema, api_schema
            )
        
        logger.info("Repair completed")
        return db_schema, ui_schema, api_schema, auth_config
    
    def _fix_missing_fields(self, errors: list[str], db_schema: dict, ui_schema: dict, api_schema: dict, auth_config: dict) -> tuple[dict, dict, dict, dict]:
        """Add missing fields with sensible defaults."""
        
        for error in errors:
            if "DB schema missing 'entities'" in error:
                db_schema["entities"] = {}
            elif "DB schema missing 'relations'" in error:
                db_schema["relations"] = []
            elif "UI schema missing 'pages'" in error:
                ui_schema["pages"] = {}
            elif "API schema missing 'endpoints'" in error:
                api_schema["endpoints"] = []
            elif "API schema missing 'base_path'" in error:
                api_schema["base_path"] = "/api/v1"
            elif "Auth config missing 'auth_type'" in error:
                auth_config["auth_type"] = "jwt"
            elif "Auth config missing 'roles'" in error:
                auth_config["roles"] = {"user": ["read", "write"]}
        
        return db_schema, ui_schema, api_schema, auth_config
    
    def _fix_consistency_issues(self, errors: list[str], db_schema: dict, ui_schema: dict, api_schema: dict) -> tuple[dict, dict, dict]:
        """Fix cross-layer consistency issues."""
        
        for error in errors:
            if "API endpoint references unknown entity" in error:
                parts = error.split(":")
                if len(parts) > 1:
                    entity_name = parts[-1].strip()
                    api_endpoints = api_schema.get("endpoints", [])
                    api_schema["endpoints"] = [
                        ep for ep in api_endpoints
                        if isinstance(ep, dict) and ep.get("entity") != entity_name
                    ]
                    logger.info(f"Removed endpoint for unknown entity: {entity_name}")
            
            elif "allows unknown role" in error:
                parts = error.split(":")
                if len(parts) > 1:
                    role_name = parts[-1].strip()
                    for endpoint in api_schema.get("endpoints", []):
                        if isinstance(endpoint, dict) and role_name in endpoint.get("allowed_roles", []):
                            endpoint["allowed_roles"] = [r for r in endpoint["allowed_roles"] if r != role_name]
                    for page in ui_schema.get("pages", {}).values():
                        if isinstance(page, dict) and role_name in page.get("allowed_roles", []):
                            page["allowed_roles"] = [r for r in page["allowed_roles"] if r != role_name]
                    logger.info(f"Removed access for unknown role: {role_name}")
        
        return db_schema, ui_schema, api_schema
    
    def _fix_logic_issues(self, errors: list[str], db_schema: dict, api_schema: dict) -> dict:
        """Fix logical issues (e.g., entities with no API access)."""
        
        db_entities = set(db_schema.get("entities", {}).keys())
        api_endpoints = api_schema.get("endpoints", [])
        
        accessed_entities = set()
        for endpoint in api_endpoints:
            if isinstance(endpoint, dict) and endpoint.get("entity"):
                accessed_entities.add(endpoint.get("entity"))
        
        unaccessed = db_entities - accessed_entities
        
        for entity in unaccessed:
            logger.info(f"Adding API endpoints for unaccessed entity: {entity}")
            
            api_schema["endpoints"].append({
                "path": f"/api/v1/{entity.lower()}s",
                "method": "GET",
                "name": f"list_{entity.lower()}",
                "description": f"List all {entity}s",
                "auth_required": True,
                "allowed_roles": ["user"],
                "entity": entity,
            })
            
            api_schema["endpoints"].append({
                "path": f"/api/v1/{entity.lower()}s",
                "method": "POST",
                "name": f"create_{entity.lower()}",
                "description": f"Create new {entity}",
                "auth_required": True,
                "allowed_roles": ["user"],
                "entity": entity,
            })
        
        return api_schema