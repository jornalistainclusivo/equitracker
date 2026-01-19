# API Documentation

This API powers the EquiTracker frontend. It is built with **FastAPI** and uses **Pydantic** for data validation.

**Base URL:** `http://localhost:8000/api/v1`

## 1. Chat & Reasoning (`/chat`)

### Chat with Source

**POST** `/chat/`

Interacts with a specific source using Retrieval Augmented Generation (RAG). The system automatically routes the intent (Summary, Fact Check, Pauta) based on the query keywords.

**Request Body:**

```json
{
  "source_uid": "string",  // UID of the source to chat with
  "query": "string"        // User question or command
}
```

**Response:**

```json
{
  "answer": "string"       // AI generated response (markdown)
}
```

---

## 2. Source Management (`/sources`)

### Create Source

**POST** `/sources/`

Register a new URL for tracking.

**Request Body:**

```json
{
  "url": "string"
}
```

### Get All Sources

**GET** `/sources/`

Returns a list of all tracked sources.

### Analyze Source

**POST** `/sources/{uid}/analyze`

Triggers the full "Sovereign Ingestion" pipeline:

1. **Scrape**: Fetches content using Crawl4AI.
2. **Vectorize**: Stores chunks in Neo4j Vector Index.
3. **Reason**: DeepSeek-R1 analyzes the content for Inclusion/Equity.

**Response:**
Returns an `AnalysisResult` object containing the `inclusion_score` and `suggested_prompts`.

### Summarize Source

**POST** `/sources/{uid}/summarize`

Generates a concise summary using the local LLM.

### Crawl Source (Manual)

**POST** `/sources/{uid}/crawl`

Manually triggers the scraping process without running the full analysis.

### Delete Source

**DELETE** `/sources/{uid}`

Removes the source and its associated data from the Graph and Vector Query.

### Delete All Sources

**DELETE** `/sources/`

**WARNING:** Destructive action. Clears the entire knowledge base.
