import os
from typing import List, Optional
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Neo4jVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.graphs import Neo4jGraph
from app.core.config import settings

class KnowledgeBase:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model="nomic-embed-text"
        )
        self.url = settings.NEO4J_URI
        self.username = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD

    async def vectorize_and_store(self, text: str, source_uid: str):
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
