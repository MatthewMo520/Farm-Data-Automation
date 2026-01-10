"""
Groq AI Service
Handles AI-powered data extraction and entity classification using Groq API
"""
from groq import AsyncGroq
from backend.core.config import settings
import logging
import json
from typing import Dict, List

logger = logging.getLogger(__name__)


class GroqService:
    """Service for Groq AI data extraction"""

    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.temperature = settings.GROQ_TEMPERATURE

    async def extract_data_from_transcription(
        self,
        transcription: str,
        schema_mappings: List[Dict]
    ) -> Dict:
        """
        Extract structured data from transcription text using Groq AI

        Args:
            transcription: Transcribed text from voice recording
            schema_mappings: List of available entity schemas for the client

        Returns:
            Dictionary with extracted data, entity type, and confidence
        """
        try:
            # Build prompt with schema information
            schema_descriptions = self._build_schema_descriptions(schema_mappings)

            system_prompt = f"""You are an AI assistant for an agricultural data management system.
Your job is to extract structured data from voice transcriptions about farm animals and operations.

Available entity types and their fields:
{schema_descriptions}

Your task:
1. Identify which entity type this transcription is about
2. Extract all relevant data fields
3. Return the data in JSON format
4. Provide a confidence score (HIGH, MEDIUM, LOW)

Rules:
- Only extract information that is explicitly mentioned
- Use null for missing fields
- Be precise with numbers, dates, and identifiers
- If the transcription doesn't match any entity type, return entity_type: "unknown"
"""

            user_prompt = f"""Transcription:
"{transcription}"

Extract the data and return ONLY a JSON object with this structure:
{{
    "entity_type": "animal|farm|treatment|unknown",
    "confidence": "HIGH|MEDIUM|LOW",
    "extracted_data": {{
        "field_name": "value",
        ...
    }},
    "notes": "any additional context or uncertainties"
}}"""

            # Call Groq API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}  # Force JSON output
            )

            # Parse response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            logger.info(f"Data extraction successful. Entity type: {result.get('entity_type')}")

            return result

        except Exception as e:
            logger.error(f"Error during Groq data extraction: {str(e)}")
            return {
                "entity_type": "unknown",
                "confidence": "LOW",
                "extracted_data": {},
                "error": str(e)
            }

    def _build_schema_descriptions(self, schema_mappings: List[Dict]) -> str:
        """Build human-readable schema descriptions for the prompt"""
        descriptions = []

        for schema in schema_mappings:
            entity_name = schema.get("entity_name", "unknown")
            field_mappings = schema.get("field_mappings", {})
            detection_keywords = schema.get("detection_keywords", [])

            fields_list = ", ".join(field_mappings.keys())
            keywords_list = ", ".join(detection_keywords) if detection_keywords else "N/A"

            desc = f"""
Entity: {entity_name}
Fields: {fields_list}
Keywords: {keywords_list}
"""
            descriptions.append(desc)

        return "\n".join(descriptions)

    async def validate_extracted_data(
        self,
        extracted_data: Dict,
        validation_rules: Dict
    ) -> Dict:
        """
        Validate extracted data against schema validation rules

        Args:
            extracted_data: Data extracted from AI
            validation_rules: Validation rules from schema mapping

        Returns:
            Dictionary with validation results and errors
        """
        errors = []
        warnings = []

        for field, rules in validation_rules.items():
            value = extracted_data.get(field)

            # Check required fields
            if rules.get("required", False) and not value:
                errors.append(f"Required field '{field}' is missing")
                continue

            if value is not None:
                # Check data type
                expected_type = rules.get("type")
                if expected_type:
                    if not self._check_type(value, expected_type):
                        errors.append(f"Field '{field}' has invalid type. Expected {expected_type}")

                # Check pattern (regex)
                pattern = rules.get("pattern")
                if pattern:
                    import re
                    if not re.match(pattern, str(value)):
                        warnings.append(f"Field '{field}' doesn't match expected pattern")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def _check_type(self, value, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_mapping = {
            "string": str,
            "integer": int,
            "float": float,
            "boolean": bool
        }

        expected_python_type = type_mapping.get(expected_type.lower())
        if not expected_python_type:
            return True  # Unknown type, skip validation

        return isinstance(value, expected_python_type)

    async def extract_with_retry(
        self,
        transcription: str,
        schema_mappings: List[Dict],
        max_retries: int = 3
    ) -> Dict:
        """
        Extract data with retry logic for rate limiting

        Args:
            transcription: Transcribed text
            schema_mappings: Available schemas
            max_retries: Maximum number of retry attempts

        Returns:
            Extraction result
        """
        import asyncio

        for attempt in range(max_retries):
            try:
                result = await self.extract_data_from_transcription(transcription, schema_mappings)

                # If we got an error in the result but no exception, check if it's a rate limit
                if result.get("error") and "rate" in result.get("error", "").lower():
                    if attempt < max_retries - 1:
                        # Exponential backoff: wait 2^attempt seconds
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limit hit, retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                        continue

                return result

            except Exception as e:
                error_message = str(e).lower()
                if "rate" in error_message and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limit exception, retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    # Non-rate-limit error or final attempt
                    raise

        # If we exhausted retries
        return {
            "entity_type": "unknown",
            "confidence": "LOW",
            "extracted_data": {},
            "error": "Max retries exceeded due to rate limiting"
        }
