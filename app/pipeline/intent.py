"""Intent extraction stage - parse natural language into structured form."""

import json
from app.services.llm_service import LLMService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IntentExtractor:
    """Extract structured intent from natural language."""
    
    def __init__(self):
        self.llm = LLMService()
    
    def extract(self, user_prompt: str) -> dict:
        """Parse user prompt into structured intent."""
        system_prompt = """You are an expert system analyst. Your job is to parse user requests for web applications into structured intent.

Extract:
1. app_name: A concise application name
2. app_description: What the app does (1-2 sentences)
3. entities: List of core entities/domains (e.g., User, Contact, Order)
4. features: List of features requested
5. auth_required: Does the app need authentication?
6. roles: What user roles exist? (admin, user, premium_user, etc.)
7. premium_features: Which features are premium-only?
8. key_pages: What pages should the app have?
9. business_logic: Important business rules or constraints
10. assumptions: What you're assuming about the request (be explicit)

Return ONLY valid JSON."""
        
        prompt = f"""User's request:
"{user_prompt}"

Extract intent as JSON with all required fields above. Be specific and practical."""
        
        schema_desc = """{{
  "app_name": "string",
  "app_description": "string",
  "entities": ["string"],
  "features": ["string"],
  "auth_required": boolean,
  "roles": ["string"],
  "premium_features": ["string"],
  "key_pages": ["string"],
  "business_logic": ["string"],
  "assumptions": ["string"]
}}"""
        
        try:
            intent = self.llm.generate_json(
                prompt=prompt,
                system=system_prompt,
                schema_description=schema_desc,
                temperature=0.7
            )
            
            required = [
                "app_name", "app_description", "entities", "features",
                "auth_required", "roles", "premium_features", "key_pages",
                "business_logic", "assumptions"
            ]
            
            missing = [f for f in required if f not in intent]
            if missing:
                logger.warning(f"Missing fields in intent: {missing}")
                for field in missing:
                    if field == "entities":
                        intent["entities"] = []
                    elif field == "features":
                        intent["features"] = []
                    elif field == "auth_required":
                        intent["auth_required"] = True
                    elif field == "roles":
                        intent["roles"] = ["user"]
                    elif field == "premium_features":
                        intent["premium_features"] = []
                    elif field == "key_pages":
                        intent["key_pages"] = []
                    elif field == "business_logic":
                        intent["business_logic"] = []
                    elif field == "assumptions":
                        intent["assumptions"] = []
                    else:
                        intent[field] = ""
            
            logger.info(f"Intent extracted: {intent['app_name']}")
            return intent
        
        except Exception as e:
            logger.error(f"Intent extraction failed: {e}")
            raise