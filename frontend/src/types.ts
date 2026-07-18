export interface Source {
    name: string;
    url: string;
    inclusion_score?: number;
    reasoning?: string;
    suggested_prompts?: string[];
    uid: string;
}

export interface SourceResponse {
    sources: Source[];
}
