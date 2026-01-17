# Architecture Documentation

## 1. The "Hybrid Brain" Concept

EquiTracker adopts a **Hybrid Brain** architecture that unifies two distinct cognitive approaches to data storage and retrieval: **Vector Memory** (Semantic) and **Graph Memory** (Contextual). This strategy addresses the limitations of purely vector-based RAG systems, which often lack the ability to understand complex, multi-hop relationships between entities.

### 1.1. Vector Memory (Semantic Search)

- **Technology**: Neo4j Vector Index (`news_vector`).
- **Engine**: Ollama (Local Embeddings using `nomic-embed-text`).
- **Purpose**: Enables semantic similarity search. When a user asks a question, the system converts the query into a vector and finds relevant text chunks that are conceptually similar, even if they don't share exact keywords.
- **Workflow**:
  1. Content is split into chunks (1000 chars).
  2. Each chunk is embedded via `OllamaEmbeddings`.
  3. Vectors are stored in Neo4j nodes (Label: `Chunk`).

### 1.2. Graph Memory (Contextual Knowledge)

- **Technology**: Neo4j (Nodes & Relationships).
- **Structure**: `(Source)-[:HAS_CHUNK]->(Chunk)`.
- **Purpose**: Maintains the structural integrity and provenance of information. It allows the system to answer questions like "What are all the reliable sources?" or "Show me the context of this specific news article," which vector search alone cannot efficiently answer.
- **Synergy**: By co-locating Vectors and the Knowledge Graph in Neo4j, we can perform hybrid queries that filter by graph properties (e.g., `source_uid`, `reliability_score`) before performing vector similarity search, drastically improving precision.

## 2. Sovereign Ingestion Pipeline

To maintain sovereignty and avoid reliance on commercial, rate-limited APIs (like generic news APIs), EquiTracker builds its own data ingestion pipeline.

### 2.1. The "No Commercial API" Rule

We strictly avoid third-party aggregator APIs. Instead, we treat the public web as our primary data source, using browser automation to act as a human-like agent.

### 2.2. Pipeline Components

1. **Crawl4AI (Sovereign Scraper)**:
    - Wraps Playwright to render modern JavaScript-heavy websites.
    - Extracts clean, readable content (Markdown/Text) from raw HTML.
    - Runs locally within the backend environment.
2. **Ingestion Service**:
    - Receives `url` input.
    - Invokes `SovereignScraper`.
    - Passes content to `KnowledgeBase` service for immediate vectorization.

## 3. Data Contracts (Schemas)

The communication between the React Frontend and FastAPI Backend is strictly typed using Pydantic models (Backend) and TypeScript Interfaces (Frontend).

### 3.1. Source Object

- **Backend (`app.schemas.source.SourceResponse`)**:

    ```python
    class SourceResponse(BaseModel):
        uid: str
        url: str
        name: str
        reliability_score: Optional[float]
        # ... other fields
    ```

- **Frontend Data Shape**:

    ```typescript
    interface Source {
        uid: string;
        url: string;
        name: string;
        reliability_score?: number; // Visualized as Percentage or "Pending"
    }
    ```

### 3.2. Reliability Analysis

- **Input**: Scraped Content + Source Metadata.

- **Process**: The system calculates a reliability score (currently a placeholder/mock, roadmap includes LLM-based evaluation).
- **Output**: A float score (0.0 to 1.0) stored on the `Source` node in Neo4j.
- **Technical Debt Note**: The reliability logic currently mocks a random score (`random.uniform(0.7, 0.95)`) in `app.api.v1.endpoints.sources.analyze_source`. This needs to be replaced with actual LLM evaluation logic.
