// [Knowledge Graph Domain Types] Matches backend schema ConceptResponse & DependencySchema
export interface Concept {
  id: number;
  document_id: number;
  name: string;
  definition: string;
  context_index?: string;
  file_url?: string;
  file_type?: string;
}

export interface Dependency {
  source: string;
  target: string;
  relation: string;
}
