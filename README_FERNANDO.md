# 🤖 AITI Assistant - Demo para Fernando

Bem-vindo! Esta é uma demonstração ao vivo do **AITI Assistant**, um chatbot RAG inteligente para atendimento ao cliente.

## 📋 O Que É

O AITI Assistant é uma solução de **Retrieval-Augmented Generation (RAG)** que:

✅ Responde perguntas baseadas em seus documentos
✅ Funciona 24/7 sem parar
✅ Integra em website, Telegram, WhatsApp
✅ Escala de 100 a 10.000+ perguntas/dia
✅ Custa ~€30-150/mês

## 🚀 Como Começar (LOCAL)

### 1. Instalar
```bash
# Clone o repo
git clone https://github.com/bilalmachraa82/aiti-assistant.git
cd aiti-assistant

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copiar config
cp .env.example .env
```

### 2. Configurar API Key

Edite o `.env` e adicione sua chave:

```bash
# Opção A: OpenAI
OPENAI_API_KEY=sk-proj-...

# Opção B: Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...

# Personalizar
COMPANY_NAME=Fernando Demo
COMPANY_LANGUAGE=pt-PT
```

### 3. Ingerir Documentos

```bash
# Documentos de exemplo (FAQs em português)
python3 ingest_demo.py

# Ou seus próprios PDFs
mkdir -p data/documents
cp seus-documentos/*.pdf data/documents/
python3 -m app.ingest
```

### 4. Iniciar Server

```bash
# Desenvolvimento (com reload)
uvicorn app.main:app --reload --port 8000

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Testar

Abra no navegador:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Demo**: http://localhost:8000/demo

### 6. Fazer Perguntas

Via cURL:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Qual é o prazo de entrega?",
    "mode": "standard"
  }'
```

Resposta esperada:
```json
{
  "response": "O prazo de entrega para Lisboa é de 24 a 48 horas úteis...",
  "confidence": 0.92,
  "sources": [
    {
      "file": "faq-exemplo.txt",
      "excerpt": "Lisboa: 24 a 48 horas úteis"
    }
  ]
}
```

## 🌐 Deploy LIVE (Railway)

### Rápido (em 5 minutos)

1. Fazer fork do repositório
2. Conectar a Railway: https://railway.app
3. Configurar variáveis (OPENAI_API_KEY, etc)
4. Deploy automático!

URL final: `https://seu-app.railway.app`

[Ver DEPLOY.md para detalhes completos]

## 📚 Documentação

### API Endpoints

#### POST /api/chat
Enviar pergunta e receber resposta.

**Request:**
```json
{
  "query": "Pergunta aqui",
  "mode": "standard",
  "conversation_id": "uuid-opcional"
}
```

**Response:**
```json
{
  "response": "Resposta...",
  "confidence": 0.85,
  "sources": [...],
  "escalate": false
}
```

#### GET /api/documents
Listar documentos indexados.

#### POST /api/documents/upload
Upload de novo documento (PDF, DOCX, TXT).

#### GET /api/health
Verificar status do serviço.

### Modes de Resposta

- **standard**: Responde se encontrar 70%+ de confiança
- **strict**: Só responde se 90%+ seguro, caso contrário escala
- **creative**: Permite mais "invenção" contextualizada

## 🎨 Integração no Website

### Widget Embed (2 linhas de código!)

```html
<script src="https://seu-app.railway.app/widget/aiti-widget.js"></script>
<script>
  AITIWidget.init({
    apiUrl: 'https://seu-app.railway.app',
    position: 'bottom-right',
    primaryColor: '#0066cc'
  });
</script>
```

Resultado: Chat flutuante apareça no seu website!

## 🔐 Segurança

✅ API keys nunca expostas no frontend
✅ Encriptação end-to-end
✅ Cumpre RGPD/LGPD
✅ Rate limiting configurável
✅ Logs de auditoria

## 💰 Preços

| Plan | Queries/mês | Preço |
|------|------------|-------|
| Starter | 10.000 | €99 |
| Professional | 50.000 | €299 |
| Enterprise | Unlimited | Custom |

**Sem contrato!** Cancele quando quiser.

## 🆘 Troubleshooting

### Erro: "No LLM API key configured"
Solução: Adicionar `OPENAI_API_KEY` ou `ANTHROPIC_API_KEY` ao `.env`

### Erro: "Database locked"
Solução: O SQLite está em uso. Apenas um processo FastAPI deve rodar por vez.

### Respostas imprecisas
Solução: Adicione mais documentos com contexto. O RAG funciona melhor com mais dados.

### Lento demais
Solução: Use `gpt-4o-mini` em vez de `gpt-4`, ou reduza `TOP_K_RESULTS` de 5 para 3.

## 📞 Suporte

- 📧 **Email**: support@aiti.dev
- 🐛 **GitHub Issues**: https://github.com/bilalmachraa82/aiti-assistant/issues
- 📚 **Documentação**: https://docs.aiti-assistant.dev

## 🎓 Próximos Passos

1. **Deploy no Railway** (~5 min)
   - Ver DEPLOY.md

2. **Customizar para seu caso de uso**
   - Mudar COMPANY_NAME
   - Alterar SYSTEM_PROMPT
   - Adicionar seus documentos

3. **Integrar widget no seu website**
   - 2 linhas de código HTML
   - Aparece como chat flutuante

4. **Monitorar uso**
   - Dashboard em /admin
   - Métricas em /api/metrics

## ⭐ Features Avançados

### Multi-idiomas
```env
COMPANY_LANGUAGE=pt-PT  # ou es, fr, en, etc
```

### Escalação para Humano
Se confidence < threshold, redireciona para fila de support.

### Analytics
```bash
curl https://seu-app.railway.app/api/metrics
```

Retorna: queries total, tempo médio, languages, top perguntas, etc.

### Feedback Loop
Usuários podem dar feedback (1-5 stars) para melhorar respostas.

---

## 📝 Licença

Proprietary © 2026 AiParaTi

---

**Aproveita a demo! Dúvidas? Escreve no chat ou contacta support@aiti.dev** 🚀
