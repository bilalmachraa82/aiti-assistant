# 🤖 AITI Assistant

**Assistente Virtual Inteligente com RAG para Atendimento ao Cliente**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

---

## 🎯 O Que É

O **AITI Assistant** é um chatbot inteligente que responde a questões de clientes usando a documentação específica da sua empresa, através de tecnologia RAG (Retrieval-Augmented Generation).

### Para Quem

- 🛒 **E-commerce**: Responde sobre produtos, stock, entregas
- 🏨 **Hotelaria**: FAQs, reservas, informações
- 💼 **Serviços**: Qualificação de leads, agendamento
- 📦 **Distribuição**: Suporte a vendedores, fichas técnicas

### Números

| Métrica | Valor |
|---------|-------|
| Taxa de resolução | >70% |
| Tempo de resposta | <3 segundos |
| Disponibilidade | 24/7 |
| ROI esperado | 200-320% |

---

## 🚀 Quick Start

### 1. Clonar e Configurar

```bash
# Clone o repositório
git clone https://github.com/bilalmachraa82/aiti-assistant.git
cd aiti-assistant

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Copiar configuração
cp .env.example .env
# Editar .env com as suas API keys
```

### 2. Configurar API Keys

Edite o ficheiro `.env`:

```env
# OpenAI ou Claude para geração
OPENAI_API_KEY=sk-...
# OU
ANTHROPIC_API_KEY=sk-ant-...

# Telegram Bot (opcional)
TELEGRAM_BOT_TOKEN=123456:ABC...

# Base de dados embeddings
DATABASE_URL=sqlite:///./aiti.db
```

### 3. Ingerir Documentos

```bash
# Criar pasta de documentos
mkdir -p data/documents

# Colocar PDFs, DOCXs, TXTs na pasta
cp ~/meus_docs/*.pdf data/documents/

# Executar ingestão
python -m app.ingest

# Output esperado:
# ✅ Processados 15 documentos
# ✅ Criados 234 chunks
# ✅ Base de conhecimento pronta!
```

### 4. Iniciar o Servidor

```bash
# Modo desenvolvimento
uvicorn app.main:app --reload --port 8000

# Modo produção
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Testar

```bash
# Testar via API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Qual o prazo de entrega?"}'

# Abrir interface web
open http://localhost:8000/demo
```

---

## 📁 Estrutura do Projecto

```
aiti-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app principal
│   ├── config.py            # Configurações
│   ├── ingest.py            # Ingestão de documentos
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py    # Geração de embeddings
│   │   ├── vectorstore.py   # Base de dados vectorial
│   │   └── chain.py         # RAG pipeline
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py          # Endpoints de chat
│   │   ├── documents.py     # Gestão de documentos
│   │   └── health.py        # Health checks
│   └── bot/
│       ├── __init__.py
│       └── telegram.py      # Bot Telegram
├── widget/
│   ├── aiti-widget.js       # Widget JavaScript
│   ├── aiti-widget.css      # Estilos do widget
│   └── demo.html            # Página de demonstração
├── data/
│   ├── documents/           # Documentos fonte
│   ├── demo/                # FAQ demo incluído
│   └── vectorstore/         # Base vectorial (SQLite)
├── docs/
│   ├── INSTALLATION.md      # Guia de instalação
│   ├── INGESTION.md         # Guia de ingestão
│   ├── API.md               # Documentação API
│   └── WIDGET.md            # Guia do widget
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔧 Componentes

### 1. Backend (FastAPI)

API REST para chat e gestão de documentos.

```python
# Exemplo de uso
import requests

response = requests.post("http://localhost:8000/api/chat", json={
    "query": "Qual o horário de funcionamento?",
    "mode": "standard"  # ou "strict"
})

print(response.json())
# {
#   "response": "O nosso horário é de segunda a sexta, das 9h às 18h.",
#   "confidence": 0.92,
#   "sources": [{"file": "horarios.pdf", "page": 1}]
# }
```

### 2. Widget JavaScript

Embed no website do cliente com 2 linhas de código.

```html
<!-- Adicionar ao website -->
<script src="https://seu-dominio.com/widget/aiti-widget.js"></script>
<script>
  AITIWidget.init({
    apiUrl: 'https://api.seu-dominio.com',
    apiKey: 'seu-api-key',
    primaryColor: '#0066cc',
    welcomeMessage: 'Olá! Como posso ajudar?',
    position: 'bottom-right'
  });
</script>
```

### 3. Bot Telegram

Atendimento directo via Telegram.

```bash
# Iniciar bot
python -m app.bot.telegram

# Utilizadores podem falar directamente com @SeuBotTelegram
```

---

## 📚 Ingestão de Documentos

### Formatos Suportados

| Formato | Extensão | Notas |
|---------|----------|-------|
| PDF | `.pdf` | Texto extraído automaticamente |
| Word | `.docx` | Preserva formatação básica |
| Texto | `.txt`, `.md` | Processamento directo |
| CSV | `.csv` | Cada linha = 1 chunk |

### Estrutura Recomendada

```
data/documents/
├── politicas/
│   ├── entregas.pdf
│   ├── devolucoes.pdf
│   └── pagamentos.pdf
├── produtos/
│   ├── catalogo-2025.pdf
│   └── fichas-tecnicas.pdf
└── faq/
    └── perguntas-frequentes.docx
```

### Comandos de Ingestão

```bash
# Ingerir todos os documentos
python -m app.ingest

# Ingerir ficheiro específico
python -m app.ingest --file data/documents/novo.pdf

# Reiniciar base (limpa tudo)
python -m app.ingest --reset

# Modo verbose
python -m app.ingest --verbose
```

---

## 🔌 API Reference

### POST /api/chat

Enviar pergunta e receber resposta.

**Request:**
```json
{
  "query": "Qual o prazo de entrega para Lisboa?",
  "mode": "standard",
  "conversation_id": "uuid-opcional"
}
```

**Response:**
```json
{
  "response": "O prazo de entrega para Lisboa é de 24-48 horas úteis.",
  "confidence": 0.89,
  "sources": [
    {
      "file": "politicas_entrega.pdf",
      "page": 2,
      "excerpt": "Lisboa e Grande Porto: 24-48h úteis..."
    }
  ],
  "conversation_id": "abc-123",
  "escalate": false
}
```

### POST /api/documents/upload

Upload de novo documento.

### GET /api/documents

Listar documentos indexados.

### DELETE /api/documents/{id}

Remover documento da base.

### GET /api/health

Verificar estado do serviço.

---

## 🐳 Docker

### Desenvolvimento

```bash
docker-compose up -d
```

### Produção

```bash
docker build -t aiti-assistant .
docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -v $(pwd)/data:/app/data \
  aiti-assistant
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

| Variável | Obrigatório | Descrição |
|----------|-------------|-----------|
| `OPENAI_API_KEY` | Sim* | API key OpenAI |
| `ANTHROPIC_API_KEY` | Sim* | API key Anthropic (alternativa) |
| `TELEGRAM_BOT_TOKEN` | Não | Token do bot Telegram |
| `DATABASE_URL` | Não | URL da base de dados (default: SQLite) |
| `EMBEDDING_MODEL` | Não | Modelo de embeddings (default: text-embedding-3-small) |
| `LLM_MODEL` | Não | Modelo LLM (default: gpt-4o-mini) |
| `CHUNK_SIZE` | Não | Tamanho dos chunks (default: 500) |
| `CHUNK_OVERLAP` | Não | Sobreposição de chunks (default: 50) |

*Uma das duas é obrigatória

---

## 📊 Métricas e Logs

O sistema gera logs estruturados e métricas:

```bash
# Ver logs
tail -f logs/aiti.log

# Métricas disponíveis em
GET /api/metrics
```

---

## 🔒 Segurança

- ✅ API keys nunca expostas no frontend
- ✅ Rate limiting configurável
- ✅ Validação de input
- ✅ CORS configurável
- ✅ Logs de auditoria

---

## 🤝 Suporte

- 📧 Email: suporte@aiparati.pt
- 📚 Docs: https://docs.aiparati.pt/aiti-assistant
- 🐛 Issues: GitHub Issues

---

## 📄 Licença

Proprietary © 2026 AiParaTi. Todos os direitos reservados.

---

*Desenvolvido com ❤️ por [AiParaTi](https://aiparati.pt)*
