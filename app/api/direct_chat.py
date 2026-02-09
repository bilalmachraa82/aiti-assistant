"""
AITI Assistant - Direct Gemini Chat (no RAG/embeddings needed)
Simple chat endpoint that uses Gemini with FAQ context.
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger()
router = APIRouter()

# Load FAQ at startup
FAQ_TEXT = ""
faq_paths = [
    "data/documents/faq-demo.txt",
    "data/demo/faq-demo.txt",
]
for p in faq_paths:
    if os.path.exists(p):
        with open(p, "r") as f:
            FAQ_TEXT = f.read()
        break

# If no FAQ found, use embedded knowledge
if not FAQ_TEXT:
    FAQ_TEXT = """
AITI - Automação Inteligente para Negócios

A AITI é uma empresa portuguesa especializada em automação inteligente para PMEs.

Soluções:
1. Automação de Processos (€4.000-€8.000 setup + €200-500/mês)
2. Chatbot RAG 24/7 (€6.000-€12.000 setup + €300-700/mês)  
3. Motor de Oportunidades (€8.000-€18.000 setup + €400-900/mês)

Resultados comprovados:
- 79% redução em tarefas manuais
- 35% aumento de faturação
- 40% redução de erros
- ROI >300% em 12 meses

Caso de Sucesso - Aurora Oceano:
- Crescimento de €2.7M para €4.4M (+60%)
- ROI de 7.235% no primeiro ano
- Tempo admin: 20h/semana → 8h/semana

Contacto: contacto@aiparati.pt
Website: https://aiparati-website.vercel.app
"""


class DirectChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    conversation_history: Optional[List[Dict[str, str]]] = None


class DirectChatResponse(BaseModel):
    response: str
    confidence: float = 0.85
    sources: List[Dict[str, Any]] = []
    provider: str = "gemini"


# Initialize Gemini
_gemini_model = None

def get_gemini():
    global _gemini_model
    if _gemini_model is None:
        try:
            import google.generativeai as genai
            api_key = os.environ.get("GEMINI_API_KEY", "")
            if api_key:
                genai.configure(api_key=api_key)
                _gemini_model = genai.GenerativeModel("gemini-2.0-flash")
                logger.info("Gemini model initialized")
            else:
                logger.error("No GEMINI_API_KEY found")
        except Exception as e:
            logger.error(f"Failed to init Gemini: {e}")
    return _gemini_model


@router.post("/chat", response_model=DirectChatResponse)
async def direct_chat(request: DirectChatRequest):
    """Direct Gemini chat with FAQ context."""
    model = get_gemini()
    if not model:
        raise HTTPException(500, "LLM not configured. Set GEMINI_API_KEY.")
    
    system = (
        "És um assistente de atendimento ao cliente da AITI. "
        "Respondes em português de Portugal (PT-PT). "
        "Sê simpático, profissional e conciso. "
        "Usa o contexto fornecido para responder. "
        "Se não souberes, diz que vais encaminhar para um colega.\n\n"
        f"CONTEXTO:\n{FAQ_TEXT}\n\n"
    )
    
    prompt = f"{system}PERGUNTA: {request.query}\n\nRESPOSTA:"
    
    try:
        response = model.generate_content(prompt)
        return DirectChatResponse(
            response=response.text.strip(),
            confidence=0.85,
            sources=[{"file": "FAQ AITI", "excerpt": "Base de conhecimento"}],
            provider="gemini"
        )
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        raise HTTPException(500, f"LLM error: {str(e)}")
