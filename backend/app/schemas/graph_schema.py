from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ConceptBase(BaseModel):
    name: str
    definition: str
    context_index: Optional[str] = None


class ConceptResponse(ConceptBase):
    id: int
    document_id: int
    file_url: Optional[str] = None
    file_type: Optional[str] = None  # FOR MORE INFORMATION ON USING <video> OR <iframe>
    model_config = ConfigDict(from_attributes=True)


class DependencySchema(BaseModel):
    source: str
    target: str
    relation: str = "prerequisite"


class GraphBuildResponse(BaseModel):
    message: str
    total_concepts: int
    dependencies_found: int
    topological_order: List[str]
