"""Application state management for ML models and services."""

import os
import pickle
import logging
from typing import Optional

import pandas as pd
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

from .config import settings

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class _SimpleConversationalRetrievalChain:
    """Compatibility wrapper for conversational retrieval flow."""

    def __init__(self, llm, retriever=None, memory=None):
        self.llm = llm
        self.retriever = retriever
        self.memory = memory

    def _retrieve_docs(self, question: str):
        if not self.retriever:
            return []
        for fn in ("get_relevant_documents", "get_documents", "retrieve", "run"):
            if hasattr(self.retriever, fn):
                try:
                    return getattr(self.retriever, fn)(question)
                except Exception:
                    continue
        try:
            return self.retriever(question)
        except Exception:
            return []

    def invoke(self, inputs: dict) -> dict:
        question = inputs.get("question") if isinstance(inputs, dict) else None
        if not question:
            logger.warning("[RAG] Empty question received")
            return {"answer": ""}

        logger.info(f"[RAG] Starting retrieval for question: '{question}'")
        docs = []
        try:
            docs = self._retrieve_docs(question) or []
            logger.info(f"[RAG] Retrieved {len(docs)} documents from vector store")
        except Exception as e:
            logger.error(f"[RAG] Error during document retrieval: {e}")
            docs = []

        context_parts = []
        for idx, d in enumerate(docs[:5], 1):
            text = None
            if hasattr(d, "page_content"):
                text = d.page_content
            elif hasattr(d, "content"):
                text = d.content
            else:
                text = str(d)
            if text:
                logger.debug(f"[RAG] Document {idx}: {text[:80]}...")
                context_parts.append(text)

        context = "\n---\n".join(context_parts)
        logger.info(f"[RAG] Total context prepared: {len(context)} chars from {len(context_parts)} documents")

        mem_text = ""
        try:
            if hasattr(self.memory, "messages"):
                mem_text = "\n".join([str(m.get("content") if isinstance(m, dict) else str(m)) 
                                     for m in getattr(self.memory, "messages", [])])
        except Exception:
            mem_text = ""

        prompt = f"""You are an assistant that answers questions using the provided context.
Context:
{context}

Conversation history:
{mem_text}

Question:
{question}

Answer concisely:
"""

        try:
            logger.debug("[RAG] Invoking LLM for answer generation...")
            raw = None
            if hasattr(self.llm, "invoke"):
                raw = self.llm.invoke(prompt)
            elif callable(self.llm):
                raw = self.llm(prompt)

            answer = ""
            if isinstance(raw, dict):
                answer = raw.get("content") or raw.get("answer") or raw.get("text") or ""
            else:
                answer = getattr(raw, "content", None) or getattr(raw, "text", None) or str(raw or "")
            if hasattr(answer, "strip"):
                answer = answer.strip()

            logger.info(f"[RAG] LLM generated answer: {len(answer)} chars")
            logger.debug(f"[RAG] Answer preview: {answer[:100]}...")

            try:
                if hasattr(self.memory, "messages"):
                    self.memory.messages.append({"role": "user", "content": question})
                    self.memory.messages.append({"role": "assistant", "content": answer})
                    logger.debug("[RAG] Memory updated with Q&A")
            except Exception:
                pass

            return {"answer": answer}
        except Exception as e:
            logger.error(f"[RAG] Error during LLM invocation: {e}")
            return {"answer": "", "error": str(e)}


class AppState:
    """Global application state holding models, chains, and services."""
    
    def __init__(self):
        self._initialize_api_clients()
        self._initialize_ml_models()
        self._initialize_search_tool()
        self._initialize_chains()
    
    def _initialize_api_clients(self) -> None:
        """Initialize external API clients (Pinecone, Google AI)."""
        try:
            logger.info("[INIT] Initializing API clients...")
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            logger.info("[INIT] Pinecone client initialized")
            self.pinecone_index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            logger.info(f"[INIT] Pinecone index '{settings.PINECONE_INDEX_NAME}' connected")
            
            self.embed_model = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=settings.GEMINI_API_KEY
            )
            logger.info("[INIT] Google Generative AI Embeddings initialized")
            
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=settings.TEMPERATURE
            )
            logger.info("[INIT] ChatGoogleGenerativeAI LLM initialized")
        except Exception as e:
            logger.error(f"[INIT] Warning: API clients could not be initialized: {e}")
            self.pinecone_index = None
            self.embed_model = None
            self.llm = None
    
    def _initialize_ml_models(self) -> None:
        """Load local ML models for classification and recommendation."""
        try:
            logger.info("[INIT] Loading ML models...")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_PATH)
            logger.info(f"[INIT] Embedding model loaded from {settings.EMBEDDING_MODEL_PATH}")
            
            with open(settings.CLASSIFICATION_MODEL_PATH, 'rb') as f:
                self.svm_classifier = pickle.load(f)
            logger.info(f"[INIT] SVM classifier loaded from {settings.CLASSIFICATION_MODEL_PATH}")
            
            with open(settings.CLUSTER_MODEL_PATH, 'rb') as f:
                self.kmeans = pickle.load(f)
            logger.info(f"[INIT] KMeans model loaded from {settings.CLUSTER_MODEL_PATH}")
            
            self.poem_df = pd.read_csv(settings.DATA_PATH)
            logger.info(f"[INIT] Poem dataset loaded from {settings.DATA_PATH} ({len(self.poem_df)} poems)")
            self._models_loaded = True
        except Exception as e:
            logger.error(f"[INIT] Warning: ML models could not be loaded. Check paths. Error: {e}")
            self.embedding_model = None
            self.svm_classifier = None
            self.kmeans = None
            self.poem_df = None
            self._models_loaded = False
    
    def _initialize_search_tool(self) -> None:
        """Initialize DuckDuckGo search tool."""
        try:
            self.search_tool = DuckDuckGoSearchResults(max_results=3)
        except Exception as e:
            print(f"Warning: Search tool could not be initialized: {e}")
            self.search_tool = None
    
    def _initialize_chains(self) -> None:
        """Initialize LangChain retrieval chains."""
        self.poet_qa_chain = self._create_retrieval_chain(settings.POET_NAMESPACE)
        self.poem_qa_chain = self._create_retrieval_chain(settings.POEM_NAMESPACE)
    
    def _create_retrieval_chain(self, namespace: str) -> Optional[object]:
        """Create a retrieval chain for a specific namespace."""
        if not self.pinecone_index or not self.embed_model or not self.llm:
            logger.warning(f"[INIT] Cannot create retrieval chain for '{namespace}': missing API clients")
            return None
            
        try:
            logger.info(f"[INIT] Creating retrieval chain for namespace: '{namespace}'")
            vectorstore = PineconeVectorStore(
                index=self.pinecone_index,
                embedding=self.embed_model,
                namespace=namespace,
            )
            logger.info(f"[INIT] PineconeVectorStore initialized for namespace '{namespace}'")
            
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            logger.info(f"[INIT] Retriever configured (k=3) for namespace '{namespace}'")
            
            # Use simple memory wrapper instead of ConversationBufferMemory
            memory = {"messages": []}
            chain = _SimpleConversationalRetrievalChain(self.llm, retriever=retriever, memory=memory)
            logger.info(f"[INIT] Retrieval chain created successfully for '{namespace}'")
            return chain
        except Exception as e:
            logger.error(f"[INIT] Error creating chain for {namespace}: {e}")
            return None
    
    @property
    def models_loaded(self) -> bool:
        """Check if ML models are loaded."""
        return getattr(self, '_models_loaded', False)


# Global singleton instance
app_state = AppState()
