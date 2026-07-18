from app.services.llm import DynamicLLMService
from langchain_core.output_parsers import PydanticOutputParser
from app.schemas.graph import GraphExtraction
import json
import logging

logger = logging.getLogger(__name__)

class EntityExtractor:
    def __init__(self):
        """
        Initialize the EntityExtractor using DynamicLLMService.
        """
        self.parser = PydanticOutputParser(pydantic_object=GraphExtraction)
        
    async def extract(self, text: str) -> GraphExtraction:
        """
        Extract entities and relationships from the given text chunk.
        """
        format_instructions = self.parser.get_format_instructions()
        
        system_prompt = f"""You are an advanced Information Extraction AI.
Extract entities (PERSON, ORG, LOCATION, TOPIC, EVENT) and relationships from the text.
Return STRICT JSON matching the following schema:
{format_instructions}

EXAMPLE INPUT:
"Google CEO Sundar Pichai announced new AI features at the I/O conference in Mountain View."

EXAMPLE OUTPUT:
{{
    "entities": [
        {{"name": "Google", "type": "ORG", "description": "Technology company"}},
        {{"name": "Sundar Pichai", "type": "PERSON", "description": "CEO of Google"}},
        {{"name": "I/O conference", "type": "EVENT", "description": "Annual developer conference"}},
        {{"name": "Mountain View", "type": "LOCATION", "description": "City in California"}},
        {{"name": "AI features", "type": "TOPIC", "description": "New product capabilities"}}
    ],
    "relationships": [
        {{"source": "Sundar Pichai", "target": "Google", "type": "CEO_OF"}},
        {{"source": "Google", "target": "I/O conference", "type": "HOSTS"}},
        {{"source": "I/O conference", "target": "Mountain View", "type": "LOCATED_AT"}}
    ]
}}
"""
        
        try:
            generated_text = await DynamicLLMService._call_provider(system_prompt, text, "json")
            
            # Clean up potential markdown formatting
            if "```json" in generated_text:
                generated_text = generated_text.split("```json")[1].split("```")[0].strip()
            elif "```" in generated_text:
                generated_text = generated_text.split("```")[0].strip()
                
            data = json.loads(generated_text)
            
            return GraphExtraction(**data)
        except Exception as e:
            logger.error(f"Failed to extract entities: {e}")
            # Return empty extraction on failure
            return GraphExtraction(entities=[], relationships=[])
