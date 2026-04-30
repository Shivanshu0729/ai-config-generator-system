"""Validation engine for generated configurations."""

import json
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Validator:
    """Validate generated configuration."""
    
    def validate(self, db_schema: dict, ui_schema: dict, api_schema: dict, auth_config: dict) -> tuple[bool, list[str]]:
        """Validate configuration schemas for consistency and correctness."""
        errors = []
        
        errors.extend(self._validate_json_structure(db_schema, ui_schema, api_schema))
        
        errors.extend(self._validate_required_fields(db_schema, ui_schema, api_schema, auth_config))
        
        errors.extend(self._validate_consistency(db_schema, ui_schema, api_schema, auth_config))
        
        errors.extend(self._validate_logic(db_schema, ui_schema, api_schema, auth_config))
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def _validate_json_structure(self, db_schema: dict, ui_schema: dict, api_schema: dict) -> list[str]:
        """Validate JSON structure is valid."""
        errors = []
        
        if not isinstance(db_schema, dict):
            errors.append("DB schema is not a dict")
        if not isinstance(ui_schema, dict):
            errors.append("UI schema is not a dict")
        if not isinstance(api_schema, dict):
            errors.append("API schema is not a dict")
        
        return errors
    
    def _validate_required_fields(self, db_schema: dict, ui_schema: dict, api_schema: dict, auth_config: dict) -> list[str]:
        """Validate all required fields are present."""
        errors = []
        
        if "entities" not in db_schema:
            errors.append("DB schema missing 'entities'")
        if "relations" not in db_schema:
            errors.append("DB schema missing 'relations'")
        
        if "pages" not in ui_schema:
            errors.append("UI schema missing 'pages'")
        
        if "endpoints" not in api_schema:
            errors.append("API schema missing 'endpoints'")
        if "base_path" not in api_schema:
            errors.append("API schema missing 'base_path'")
        
        if "auth_type" not in auth_config:
            errors.append("Auth config missing 'auth_type'")
        if "roles" not in auth_config:
            errors.append("Auth config missing 'roles'")
        
        return errors
    
    def _validate_consistency(self, db_schema: dict, ui_schema: dict, api_schema: dict, auth_config: dict) -> list[str]:
        """Validate cross-layer consistency.
        
        Rules:
        - API endpoints must map to DB entities
        - UI components must bind to valid fields
        - API roles must match auth_config roles
        """
        errors = []
        
        db_entities = set(db_schema.get("entities", {}).keys())
        ui_pages = set(ui_schema.get("pages", {}).keys())
        api_endpoints = api_schema.get("endpoints", [])
        auth_roles = set(auth_config.get("roles", {}).keys())
        
        for endpoint in api_endpoints:
            if isinstance(endpoint, dict):
                entity = endpoint.get("entity")
                if entity and entity not in db_entities:
                    errors.append(f"API endpoint references unknown entity: {entity}")
                
                allowed_roles = endpoint.get("allowed_roles", [])
                for role in allowed_roles:
                    if role not in auth_roles:
                        errors.append(f"API endpoint allows unknown role: {role}")
        
        for page_name, page in ui_schema.get("pages", {}).items():
            if isinstance(page, dict):
                allowed_roles = page.get("allowed_roles", [])
                for role in allowed_roles:
                    if role not in auth_roles:
                        errors.append(f"UI page '{page_name}' allows unknown role: {role}")
        
        return errors
    
    def _validate_logic(self, db_schema: dict, ui_schema: dict, api_schema: dict, auth_config: dict) -> list[str]:
        """Validate logical rules.
        
        Rules:
        - Premium features should map to premium_user role
        - All entities should have at least one access method (API or UI)
        """
        errors = []
        
        db_entities = set(db_schema.get("entities", {}).keys())
        api_endpoints = api_schema.get("endpoints", [])
        
        accessed_entities = set()
        for endpoint in api_endpoints:
            if isinstance(endpoint, dict) and endpoint.get("entity"):
                accessed_entities.add(endpoint.get("entity"))
        
        for entity in db_entities:
            if entity not in accessed_entities:
                logger.warning(f"DB entity '{entity}' has no API access")
        
        return errors