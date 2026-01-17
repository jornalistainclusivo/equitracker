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
        prompt = ChatPromptTemplate.from_template("""
You are the EquiTracker Intelligence, specialized in analyzing media through the lens of Human Rights, Intersectionality, and Anti-Ableism (LBI - Lei Brasileira de Inclusão).

CONTEXT FROM SOURCE:
{context}

USER QUERY:
{input}

INSTRUCTIONS:
Analyze the provided context strictly. Use your chain-of-thought to verify:
1. **Language:** Are there euphemisms (e.g., "special needs") or capacitist terms?
2. **Agency:** are PwD (People with Disabilities) portrayed as objects of pity/overcoming or as subjects of rights?
3. **Legislation:** Does the content align with the principles of the LBI (autonomy, accessibility)?

OUTPUT FORMAT (Markdown):
Using Portuguese (Brazil), provide a structured response (do not output the internal reasoning trace in the final response, just the result):

## 🎯 Análise Objetiva
[Direct answer to the user query]

## 👁️ Lupa de Equidade (JINC)
* **Viés Detectado:** [Point out specific terms or framings]
* **Pontos Fortes:** [What did the text get right?]
* **Contexto Legal:** [Connection to LBI or Human Rights]

## 💡 Sugestão de Enquadramento
[How to rewrite/improve this narrative]
""")

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
