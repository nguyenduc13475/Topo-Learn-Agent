from pydantic import BaseModel
from typing import List, Optional


class ConceptBase(BaseModel):
    name: str
    definition: str
    context_index: Optional[str] = None


class ConceptResponse(ConceptBase):
    id: int
    document_id: int

    class Config:
        from_attributes = True


class DependencySchema(BaseModel):
    source: str
    target: str
    relation: str = "prerequisite"


class GraphBuildResponse(BaseModel):
    message: str
    total_concepts: int
    dependencies_found: int
    topological_order: List[str]
