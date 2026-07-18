import os
from typing import List, Optional, Dict, Any
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Neo4jVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_neo4j import Neo4jGraph
from app.core.config import settings

class KnowledgeBase:
    def __init__(self) -> None:
        self.embeddings = OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_EMBED_MODEL
        )
        self.url = settings.NEO4J_URI
        self.username = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD

    async def vectorize_and_store(self, text: str, source_uid: str) -> None:
        """
        Chunks the text, creates embeddings, and stores them in Neo4j.
        Connects chunks to the Source node via HAS_CHUNK relationship.
        """
        if not text:
            return

        # 1. Chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        chunks = text_splitter.split_text(text)

        # 2. Embedding & Storage (using Neo4jVector)
        # We use from_texts to store vectors.
        # Neo4jVector automatically creates nodes (default label "Chunk") and index.
        # We need to make sure we can identify these chunks to link them.
        # Strategy: Pass source_uid in metadata for each chunk.
        
        metadatas = [{"source_uid": source_uid} for _ in chunks]

        vector_store = Neo4jVector.from_texts(
            texts=chunks,
            embedding=self.embeddings,
            url=self.url,
            username=self.username,
            password=self.password,
            index_name="news_vector",
            metadatas=metadatas,
            # We can map standard node label. Default is 'Chunk'.
            # We will use that.
        )

        # 3. Graph Connection
        # LangChain creates nodes with label `Chunk` (by default) and properties `text`, `embedding`, and metadata fields.
        # So it will have `source_uid` property.
        # We can run a Cypher query to link them.
        
        graph = Neo4jGraph(
            url=self.url,
            username=self.username,
            password=self.password
        )
        
        query = """
        MATCH (s:Source {uid: $uid})
        MATCH (c:Chunk {source_uid: $uid})
        MERGE (s)-[:HAS_CHUNK]->(c)
        """
        graph.query(query, params={"uid": source_uid})

    async def hybrid_search(self, query: str, source_uid: str, top_k: int = 3) -> str:
        """
        Performs a hybrid search (Vector + Graph) to build context for a query.
        Returns a combined context string.
        """
        # 1. Vector Search for relevant chunks
        vector_store = Neo4jVector.from_existing_index(
            embedding=self.embeddings,
            url=self.url,
            username=self.username,
            password=self.password,
            index_name="news_vector",
        )
        
        # Filter by source_uid if possible, or just search and filter in memory
        # In langchain Neo4jVector we can pass a filter dict if supported, but let's do a basic search
        # and filter by metadata
        docs = vector_store.similarity_search(query, k=top_k * 3) # fetch more to filter
        
        relevant_chunks = [doc.page_content for doc in docs if doc.metadata.get("source_uid") == source_uid][:top_k]
        
        # 2. Graph Traversal for Entities
        graph = Neo4jGraph(
            url=self.url,
            username=self.username,
            password=self.password
        )
        
        cypher_query = """
        MATCH (s:Source {uid: $uid})-[:MENTIONS]->(e:Entity)
        OPTIONAL MATCH (e)-[r]->(other:Entity)
        RETURN e.name AS entity, e.type AS type, type(r) AS rel, other.name AS target
        LIMIT 50
        """
        
        results = graph.query(cypher_query, params={"uid": source_uid})
        
        # 3. Combine Context
        context_parts = []
        if relevant_chunks:
            context_parts.append("TRECHOS RELEVANTES DO TEXTO:")
            for i, chunk in enumerate(relevant_chunks, 1):
                context_parts.append(f"[{i}] {chunk}")
                
        if results:
            context_parts.append("\nENTIDADES E RELACIONAMENTOS EXTRAÍDOS (GRAFO):")
            entities_added = set()
            for row in results:
                entity = f"{row['entity']} ({row['type']})"
                if entity not in entities_added:
                    context_parts.append(f"- {entity}")
                    entities_added.add(entity)
                
                if row['rel'] and row['target']:
                    context_parts.append(f"  -> {row['rel']} -> {row['target']}")
                    
        return "\n".join(context_parts)
