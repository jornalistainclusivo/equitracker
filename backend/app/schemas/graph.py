from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class Entity(BaseModel):
    name: str = Field(..., description="Name of the entity")
    type: Literal["PERSON", "ORG", "LOCATION", "TOPIC", "EVENT"]
    description: Optional[str] = Field(None, description="Brief context")

class Relationship(BaseModel):
    source: str = Field(..., description="Name of the source entity")
    target: str = Field(..., description="Name of the target entity")
    type: str = Field(..., description="Relationship type (e.g., EMPLOYS, LOCATED_IN, MENTIONED)")
    
class GraphExtraction(BaseModel):
    entities: List[Entity]
    relationships: List[Relationship]
