export interface Source {
    name: string;
    url: string;
    reliability_score: number;
}

export interface SourceResponse {
    sources: Source[];
}
