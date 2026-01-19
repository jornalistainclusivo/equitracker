# Architecture Documentation

## 1. The "Hybrid Brain" Concept

EquiTracker adopts a **Hybrid Brain** architecture that unifies two distinct cognitive approaches to data storage and retrieval: **Vector Memory** (Semantic) and **Graph Memory** (Contextual). This strategy addresses the limitations of purely vector-based RAG systems.

### 1.1. Vector Memory (Semantic Search)

- **Technology**: Neo4j Vector Index (`news_vector`).
- **Engine**: Ollama (Local Embeddings using `nomic-embed-text`).
- **Purpose**: Enables semantic similarity search (finding concepts, not just keywords).
- **Workflow**:
  1. Content is split into chunks (1000 chars).
  2. Each chunk is embedded via `OllamaEmbeddings`.
  3. Vectors are stored in Neo4j nodes (Label: `Chunk`).

### 1.2. Graph Memory (Contextual Knowledge)

- **Technology**: Neo4j (Nodes & Relationships).
- **Structure**: `(Source)-[:HAS_CHUNK]->(Chunk)`.
- **Purpose**: Maintains structural integrity and provenance.
- **Synergy**: Co-locating Vectors and Knowledge Graph allows hybrid queries (filtering by graph properties before vector search).

### 1.3. Reasoning Engine (Local Intelligence)

- **Models**:
  - **DeepSeek-R1 (8b)**: Used for complex RAG reasoning, Chat interactions, and Fact Checking.
  - **Gemma 2 (2b)**: Used for lightweight tasks like summarization and raw inclusion scoring.
- **Sovereignty**: All models run locally via Ollama with zero data egress.

## 2. Sovereign Ingestion Pipeline

To maintain sovereignty, EquiTracker builds its own data ingestion pipeline.

### 2.1. The "No Commercial API" Rule

We strictly avoid third-party aggregator APIs. We treat the public web as our primary data source.

### 2.2. Pipeline Components

1. **Crawl4AI (Sovereign Scraper)**:
    - Wraps Playwright to render modern JavaScript-heavy websites.
    - Extracts clean Markdown/Text from raw HTML.
2. **Analysis Service (`OllamaService`)**:
    - **Inclusion Scan**: Scans content for bias using a dedicated rubric (0-100 score).
    - **Prompt Generation**: Dynamically suggests 3 "Data Void" questions based on the text.
3. **Ingestion**:
    - Stores raw content, vector embeddings, and analysis results in Neo4j.

## 3. Data Contracts (Schemas)

Communication between Frontend and Backend is strictly typed.

### 3.1. Source Object

- **Backend (`app.schemas.source.SourceResponse`)**:

    ```python
    class SourceResponse(BaseModel):
        uid: str
        url: str
        name: str
        reliability_score: Optional[float]
        # ...
    ```

### 3.2. Reliability & Inclusion Analysis

- **Input**: Scraped Content.
- **Process**: LLM-based evaluation (`analyze_article` in `llm.py`).
- **Output**:
  - `inclusion_score`: 0-100 (Integer).
  - `suggested_prompts`: List of strings.
