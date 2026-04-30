import json
import os
from typing import Any
from groq import Groq

from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """Wrapper around the Groq API with structured output support."""

    def __init__(self, model: str = "llama-3.1-8b-instant"):
        """Initialize the LLM service with safe model handling."""
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        self.client = Groq(api_key=api_key)

        self.model = os.getenv("GROQ_MODEL", model)

        supported_models = [
            "llama-3.1-8b-instant",   
            "llama-3.3-70b-versatile"    
        ]

        if self.model not in supported_models:
            logger.warning(
                f"Model '{self.model}' not supported. Falling back to 'llama-3.1-8b-instant'"
            )
            self.model = "llama-3.1-8b-instant"

        self.max_retries = 3

    def generate_json(
        self,
        prompt: str,
        system: str = "",
        schema_description: str = "",
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Generate structured JSON output from the LLM."""

        full_system = system

        if schema_description:
            full_system += f"\n\nExpected JSON structure:\n{schema_description}"

        full_system += "\n\nIMPORTANT: Return ONLY valid JSON. No explanation, no markdown."

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=4096,
                    messages=[
                        {"role": "system", "content": full_system},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                )

                output = response.choices[0].message.content.strip()

                if output.startswith("```"):
                    output = output.split("```")[1].strip()
                    if output.startswith("json"):
                        output = output[4:].strip()

                data = json.loads(output)

                logger.info(f"LLM JSON generation success (attempt {attempt+1})")
                return data

            except json.JSONDecodeError as e:
                logger.warning(f"Attempt {attempt + 1}: JSON parsing failed: {e}")

                prompt = prompt + "\n\nReturn ONLY valid JSON."

            except Exception as e:
                logger.error(f"Attempt {attempt + 1}: LLM error: {e}")

                if attempt == self.max_retries - 1:
                    raise

        raise ValueError("Failed to generate valid JSON after retries")

    def generate_text(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
    ) -> str:
        """Generate plain text output from LLM."""

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )

        return response.choices[0].message.content.strip()