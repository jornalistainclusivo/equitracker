from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.core.config import settings
from app.schemas.graph import GraphExtraction

class EntityExtractor:
    def __init__(self, model: str = "deepseek-r1:8b"):
        """
        Initialize the EntityExtractor with a local Ollama model.
        Defaults to 'deepseek-r1:8b' as per project standards, but customizable.
        """
        self.llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=model,
            format="json",
            temperature=0
        )
        self.parser = PydanticOutputParser(pydantic_object=GraphExtraction)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an advanced Information Extraction AI.
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
"""),
            ("human", "{text}")
        ])

    async def extract(self, text: str) -> GraphExtraction:
        """
        Extract entities and relationships from the given text chunk.
        """
        chain = self.prompt | self.llm | self.parser
        return await chain.ainvoke({
            "text": text,
            "format_instructions": self.parser.get_format_instructions()
        })
