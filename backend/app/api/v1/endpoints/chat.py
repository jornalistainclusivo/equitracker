from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import Neo4jVector
try:
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
except ImportError:
    # Fallback for environments where langchain.chains is moved/renamed (e.g. langchain-classic)
    from langchain_classic.chains import create_retrieval_chain
    from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

router = APIRouter()

class ChatRequest(BaseModel):
    source_uid: str
    query: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/", response_model=ChatResponse)
async def chat_with_source(request: ChatRequest):
    """
    Chat with a specific source using RAG.
    Uses LangChain v0.3+ LCEL chains.
    """
    try:
        # 1. Initialize Embeddings (must match ingestion)
        embeddings = OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model="nomic-embed-text"
        )

        # 2. Connect to Neo4j Vector Store (Existing Index)
        vector_store = Neo4jVector.from_existing_index(
            embedding=embeddings,
            url=settings.NEO4J_URI,
            username=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD,
            index_name="news_vector",
        )

        # 3. Initialize LLM
        llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model="deepseek-r1:8b", 
            temperature=0.1
        )

        # 4. Create Prompt Template
        # 4. Determine System Prompt based on Intent
        from app.services.llm import get_system_prompt

        user_message_lower = request.query.lower()
        if "resumo" in user_message_lower:
            intent = "summary"
        elif "verificar fatos" in user_message_lower:
            intent = "fact_check"
        elif "pauta" in user_message_lower:
            intent = "pauta"
        else:
            intent = "default"

        system_template = get_system_prompt(intent)
        
        # Append context placeholder for RAG
        system_template += "\n\nCONTEXT:\n{context}"
        
        if intent == "default":
             system_template += "\n\nUSER QUERY:\n{input}"

        prompt = ChatPromptTemplate.from_template(system_template)

        # 5. Create Document Chain (Stuff)
        document_chain = create_stuff_documents_chain(llm, prompt)

        # 6. Create Retrieval Chain with source filtering
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 3,
                "filter": {"source_uid": request.source_uid}
            }
        )
        
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        # 7. Execute Chain
        # Note: create_retrieval_chain expects "input" as key
        result = retrieval_chain.invoke({"input": request.query})
        
        return {"answer": result["answer"]}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
