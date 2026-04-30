"""System design stage - convert intent to architecture."""

import json
from app.services.llm_service import LLMService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SystemDesigner:
    """Design application architecture from intent."""
    
    def __init__(self):
        self.llm = LLMService()
    
    def design(self, intent: dict) -> dict:
        """Create system design from intent."""
        system_prompt = """You are a system architect. Your job is to convert intent into a detailed technical design.

For each entity, define:
1. Entity name
2. Attributes and their purposes
3. Relationships with other entities
4. Who can access/modify it

Define user flows for each major feature.
Define page layout and navigation.
Define API patterns (RESTful resources).

Return ONLY valid JSON."""
        
        entities_list = ", ".join(intent.get("entities", []))
        features_list = ", ".join(intent.get("features", []))
        
        prompt = f"""Application: {intent.get('app_name', 'App')}
Description: {intent.get('app_description', '')}

Entities: {entities_list}
Features: {features_list}
Roles: {', '.join(intent.get('roles', []))}
Premium features: {', '.join(intent.get('premium_features', []))}

Design the application:
1. For each entity, define its attributes with types and purposes
2. Define relationships between entities
3. For each feature, describe the user flow
4. Design the page structure
5. Define API endpoints needed

Return design as JSON with keys:
- entities (dict with entity designs)
- relationships (list of how entities relate)
- user_flows (dict of feature -> flow description)
- pages (list of page definitions with routes)
- api_patterns (list of REST patterns)
- access_rules (how roles affect data access)"""
        
        schema_desc = """{{
  "entities": {{}},
  "relationships": [],
  "user_flows": {{}},
  "pages": [],
  "api_patterns": [],
  "access_rules": {{}}
}}"""
        
        try:
            design = self.llm.generate_json(
                prompt=prompt,
                system=system_prompt,
                schema_description=schema_desc,
                temperature=0.7
            )
            
            if "entities" not in design:
                design["entities"] = {}
            if "relationships" not in design:
                design["relationships"] = []
            if "user_flows" not in design:
                design["user_flows"] = {}
            if "pages" not in design:
                design["pages"] = []
            if "api_patterns" not in design:
                design["api_patterns"] = []
            if "access_rules" not in design:
                design["access_rules"] = {}
            
            logger.info(f"Design created: {len(design.get('entities', {}))} entities, {len(design.get('pages', []))} pages")
            return design
        
        except Exception as e:
            logger.error(f"Design stage failed: {e}")
            raise