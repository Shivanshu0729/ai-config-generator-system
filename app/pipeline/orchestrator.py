"""Pipeline orchestrator for application configuration generation."""

import json
from app.pipeline.intent import IntentExtractor
from app.pipeline.design import SystemDesigner
from app.pipeline.schema import SchemaGenerator
from app.pipeline.validator import Validator
from app.pipeline.repair import RepairEngine
from app.models.schema_models import GeneratedConfig
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:
    """Orchestrates the complete generation pipeline."""
    
    def __init__(self, max_repair_attempts: int = 3):
        self.intent_extractor = IntentExtractor()
        self.designer = SystemDesigner()
        self.schema_gen = SchemaGenerator()
        self.validator = Validator()
        self.repair_engine = RepairEngine()
        self.max_repair_attempts = max_repair_attempts
        
        self.metrics = {
            "intent_time": 0,
            "design_time": 0,
            "schema_time": 0,
            "validation_time": 0,
            "repair_attempts": 0,
            "success": False,
            "total_time": 0,
        }
    
    def run(self, user_prompt: str) -> dict:
        """Execute the generation pipeline."""
        import time
        start_time = time.time()
        
        try:
            logger.info(f"Generating config from prompt: {user_prompt[:80]}...")
            
            intent = self.intent_extractor.extract(user_prompt)
            logger.info(f"Intent extracted: app_name={intent.get('app_name')}")
            
            design = self.designer.design(intent)
            logger.info(f"Design created with {len(design.get('entities', {}))} entities")
            
            schemas = self.schema_gen.generate(intent, design)
            db_schema = schemas["db_schema"]
            ui_schema = schemas["ui_schema"]
            api_schema = schemas["api_schema"]
            auth_config = schemas["auth_config"]
            logger.info("Schemas generated successfully")
            
            logger.info("Starting validation and repair loop")
            attempt = 0
            while attempt < self.max_repair_attempts:
                attempt += 1
                
                is_valid, errors = self.validator.validate(
                    db_schema, ui_schema, api_schema, auth_config
                )
                
                if is_valid:
                    logger.info(f"Validation passed on attempt {attempt}")
                    self.metrics["success"] = True
                    break
                
                logger.warning(f"Validation failed with {len(errors)} errors")
                for error in errors[:3]:
                    logger.warning(f"  {error}")
                
                if attempt < self.max_repair_attempts:
                    logger.info(f"Attempting repair ({attempt}/{self.max_repair_attempts})...")
                    db_schema, ui_schema, api_schema, auth_config = self.repair_engine.repair(
                        errors, db_schema, ui_schema, api_schema, auth_config, intent
                    )
                    self.metrics["repair_attempts"] += 1
                else:
                    logger.error("Max repair attempts reached")
                    raise ValueError(f"Validation failed after {self.max_repair_attempts} attempts")
            
            logger.info("\n[Final] Building complete configuration...")
            config = {
                "app_name": intent.get("app_name", "Generated App"),
                "app_description": intent.get("app_description", ""),
                "entities": db_schema.get("entities", {}),
                "db_schema": db_schema,
                "ui_schema": ui_schema,
                "api_schema": api_schema,
                "auth_config": auth_config,
                "assumptions": intent.get("assumptions", []),
                "notes": f"Generated with {self.metrics['repair_attempts']} repair iterations",
            }
            
            logger.info("\n=== GENERATION SUCCESSFUL ===")
            self.metrics["total_time"] = time.time() - start_time
            logger.info(f"Total time: {self.metrics['total_time']:.2f}s")
            
            return {
                "success": True,
                "config": config,
                "metrics": self.metrics,
            }
        
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            self.metrics["total_time"] = time.time() - start_time
            
            return {
                "success": False,
                "error": str(e),
                "metrics": self.metrics,
            }