export interface Source {
    name: string;
    url: string;
    reliability: number;
    uid: string;
}

export interface SourceResponse {
    sources: Source[];
}
