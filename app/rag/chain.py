"""
AITI Assistant - RAG Chain
Main RAG pipeline that combines retrieval and generation.
"""

from typing import List, Dict, Any, Optional
import openai
import anthropic
import google.generativeai as genai
import structlog

from app.config import settings
from app.rag.vectorstore import VectorStore

logger = structlog.get_logger()


class RAGChain:
    """RAG pipeline combining retrieval and generation."""
    
    def __init__(self, vectorstore: VectorStore):
        """
        Initialize the RAG chain.
        
        Args:
            vectorstore: The vector store for document retrieval
        """
        self.vectorstore = vectorstore
        self.provider = settings.get_llm_provider()
        
        # Initialize LLM client
        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
        elif self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        elif self.provider == "gemini":
            genai.configure(api_key=settings.gemini_api_key)
            self.client = genai.GenerativeModel("gemini-2.0-flash")
    
    def query(
        self,
        query: str,
        mode: str = "standard",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a query through the RAG pipeline.
        
        Args:
            query: The user's question
            mode: "standard" or "strict" (strict only uses retrieved context)
            conversation_history: Optional list of previous messages
            
        Returns:
            Dictionary with response, sources, confidence, etc.
        """
        # 1. Retrieve relevant documents
        retrieved_docs = self.vectorstore.search(query)
        
        logger.info(
            "Documents retrieved",
            query=query[:50],
            count=len(retrieved_docs),
            top_score=retrieved_docs[0]["score"] if retrieved_docs else 0
        )
        
        # 2. Build context from retrieved documents
        context = self._build_context(retrieved_docs)
        
        # 3. Generate response
        response_text = self._generate_response(
            query=query,
            context=context,
            mode=mode,
            conversation_history=conversation_history
        )
        
        # 4. Calculate confidence and check for escalation
        confidence = self._calculate_confidence(retrieved_docs)
        escalate = confidence < settings.confidence_threshold and mode == "strict"
        
        # 5. Format sources
        sources = self._format_sources(retrieved_docs)
        
        return {
            "response": response_text,
            "confidence": confidence,
            "sources": sources,
            "escalate": escalate,
            "mode": mode,
            "retrieved_count": len(retrieved_docs)
        }
    
    def _build_context(self, docs: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        if not docs:
            return "Não foram encontrados documentos relevantes na base de conhecimento."
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc["metadata"].get("source", "Documento")
            page = doc["metadata"].get("page", "")
            page_str = f", página {page}" if page else ""
            
            context_parts.append(
                f"[Fonte {i}: {source}{page_str}]\n{doc['text']}"
            )
        
        return "\n\n".join(context_parts)
    
    def _generate_response(
        self,
        query: str,
        context: str,
        mode: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using the LLM."""
        # Build system prompt
        system_prompt = settings.formatted_system_prompt
        
        if mode == "strict":
            system_prompt += (
                "\n\nIMPORTANTE: Responde APENAS com base nos documentos fornecidos. "
                "Se a informação não estiver nos documentos, diz: "
                "'Não encontrei esta informação nos nossos documentos. "
                "Vou encaminhar a sua questão para um colega que poderá ajudar melhor.'"
            )
        
        # Build user message with context
        user_message = f"""CONTEXTO DOS DOCUMENTOS:
{context}

PERGUNTA DO CLIENTE: {query}

RESPOSTA:"""
        
        # Build messages
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        messages.append({"role": "user", "content": user_message})
        
        # Generate with appropriate provider
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # or settings.llm_model
                max_tokens=1000,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text.strip()
        
        elif self.provider == "gemini":
            # Build full prompt for Gemini
            full_prompt = f"{system_prompt}\n\n{user_message}"
            response = self.client.generate_content(full_prompt)
            return response.text.strip()
        
        raise ValueError(f"Unknown provider: {self.provider}")
    
    def _calculate_confidence(self, docs: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on retrieval results."""
        if not docs:
            return 0.0
        
        # Use average of top 3 scores
        top_scores = [doc["score"] for doc in docs[:3]]
        return sum(top_scores) / len(top_scores)
    
    def _format_sources(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources for the response."""
        sources = []
        seen = set()
        
        for doc in docs:
            source = doc["metadata"].get("source", "Unknown")
            page = doc["metadata"].get("page", None)
            
            # Avoid duplicates
            key = f"{source}:{page}"
            if key in seen:
                continue
            seen.add(key)
            
            sources.append({
                "file": source,
                "page": page,
                "excerpt": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"],
                "score": round(doc["score"], 3)
            })
        
        return sources[:5]  # Top 5 sources
