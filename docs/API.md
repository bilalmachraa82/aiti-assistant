# API Reference - AITI Assistant

## Base URL

```
http://localhost:8000/api
```

Produção: `https://api.seu-dominio.com/api`

---

## Autenticação

Se configurado `API_KEY` no `.env`, inclua o header:

```
Authorization: Bearer sua-api-key
```

---

## Endpoints

### Chat

#### POST /chat

Enviar pergunta e receber resposta do assistente.

**Request:**
```json
{
  "query": "Qual o prazo de entrega para Lisboa?",
  "mode": "standard",
  "conversation_id": "uuid-opcional",
  "conversation_history": []
}
```

**Parâmetros:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `query` | string | Sim | Pergunta do utilizador (1-2000 chars) |
| `mode` | string | Não | `standard` ou `strict` (default: standard) |
| `conversation_id` | string | Não | ID da conversa para manter contexto |
| `conversation_history` | array | Não | Mensagens anteriores |

**Response:**
```json
{
  "response": "O prazo de entrega para Lisboa é de 24 a 48 horas úteis.",
  "confidence": 0.89,
  "sources": [
    {
      "file": "prazos-entrega.pdf",
      "page": 1,
      "excerpt": "Lisboa e Porto: 24-48 horas úteis...",
      "score": 0.92
    }
  ],
  "escalate": false,
  "conversation_id": "abc-123",
  "timestamp": "2026-02-04T12:00:00Z"
}
```

**Modos:**
- `standard`: Responde com base nos documentos, complementa com conhecimento geral se necessário
- `strict`: Responde APENAS com base nos documentos. Se não encontrar, sugere escalonamento.

---

#### GET /chat/{conversation_id}

Obter histórico de uma conversa.

**Response:**
```json
{
  "conversation_id": "abc-123",
  "messages": [
    {"role": "user", "content": "Olá"},
    {"role": "assistant", "content": "Olá! Como posso ajudar?"}
  ]
}
```

---

#### DELETE /chat/{conversation_id}

Eliminar uma conversa.

---

#### POST /chat/feedback

Submeter feedback sobre uma resposta.

**Request:**
```json
{
  "conversation_id": "abc-123",
  "message_index": 1,
  "rating": 5,
  "comment": "Resposta muito útil!"
}
```

---

### Documents

#### POST /documents/upload

Upload de novo documento.

**Request:** `multipart/form-data`
- `file`: Ficheiro (PDF, DOCX, TXT, MD, CSV)
- `category`: Categoria opcional

**Response:**
```json
{
  "status": "success",
  "document": {
    "id": "doc-123",
    "filename": "novo-documento.pdf",
    "status": "uploaded"
  }
}
```

---

#### GET /documents

Listar todos os documentos.

**Response:**
```json
[
  {
    "id": "doc-123",
    "filename": "faq.pdf",
    "file_type": ".pdf",
    "size_bytes": 102400,
    "chunks_count": 15,
    "status": "indexed"
  }
]
```

---

#### GET /documents/stats

Estatísticas dos documentos.

**Response:**
```json
{
  "total_documents": 10,
  "total_chunks": 150,
  "file_types": {".pdf": 5, ".txt": 3, ".docx": 2}
}
```

---

#### GET /documents/{id}

Detalhes de um documento.

---

#### DELETE /documents/{id}

Remover documento e seus chunks.

---

### Health

#### GET /health

Estado geral do serviço.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-04T12:00:00Z",
  "components": {
    "vectorstore": {"status": "healthy", "document_count": 150},
    "llm": {"status": "configured", "provider": "openai"},
    "telegram": {"status": "configured"}
  }
}
```

---

#### GET /health/live

Probe de liveness (Kubernetes).

---

#### GET /health/ready

Probe de readiness (Kubernetes).

---

#### GET /metrics

Métricas do serviço.

---

## Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 400 | Request inválido |
| 401 | Não autenticado |
| 404 | Recurso não encontrado |
| 429 | Rate limit excedido |
| 500 | Erro interno |

**Formato de erro:**
```json
{
  "detail": "Descrição do erro"
}
```

---

## Rate Limiting

Por defeito:
- 60 requests/minuto por IP
- 1000 requests/hora por API key

---

## Exemplos

### cURL

```bash
# Chat simples
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Qual o prazo de entrega?"}'

# Com autenticação
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sua-api-key" \
  -d '{"query": "Qual o prazo de entrega?", "mode": "strict"}'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "query": "Qual o prazo de entrega?",
        "mode": "standard"
    }
)

data = response.json()
print(data["response"])
print(f"Confiança: {data['confidence']}")
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Qual o prazo de entrega?'
  })
});

const data = await response.json();
console.log(data.response);
```

---

## Telegram Bot

### Configurar

1. Crie bot com [@BotFather](https://t.me/botfather)
2. Copie o token
3. Configure no `.env`:
```env
TELEGRAM_BOT_TOKEN=123456:ABC...
```

### Executar

```bash
python -m app.bot.telegram
```

### Comandos Suportados

| Comando | Descrição |
|---------|-----------|
| `/start` | Iniciar conversa |
| `/help` | Ver ajuda |
| `/novo` | Nova conversa |
| `/humano` | Falar com atendente |

### Docker

```bash
docker-compose --profile telegram up -d
```
