# 🚀 Guia de Deploy - AITI Assistant no Railway

**Status:** ✅ Pronto para Deploy  
**Data:** 08 Fev 2026  
**Versão:** v1.0  

---

## 📋 Pré-Requisitos

- ✅ Node.js 18+ (para Railway CLI)
- ✅ Git configurado
- ✅ Conta Railway (grátis em https://railway.app)
- ❌ **REQUER:** OPENAI_API_KEY ou ANTHROPIC_API_KEY

---

## 🔐 BLOQUEADOR CRÍTICO

**Sem uma API key válida, o chatbot não conseguirá responder a queries.**

### Como obter API Key

#### OpenAI (Recomendado)
1. Ir a https://platform.openai.com/api-keys
2. Criar chave nova
3. Copiar valor `sk-proj-...`
4. Adicionar crédito pago (sem trial grátis)

#### Anthropic (Alternativa)
1. Ir a https://console.anthropic.com/
2. Criar chave nova
3. Copiar valor `sk-ant-...`

---

## 🚀 PASSO 1: Instalar Railway CLI

```bash
npm install -g @railway/cli

# Verificar instalação
railway --version
```

---

## 🚀 PASSO 2: Login no Railway

```bash
railway login
# Abre browser → Autenticar com GitHub/Google/Email
# Confirmar no terminal
```

---

## 🚀 PASSO 3: Criar Projeto Railway

```bash
cd /home/ubuntu/clawd/projects/aiti-assistant

# Opção A: Novo projeto
railway init
# Seguir prompts → Criar novo projeto → Nome "aiti-assistant"

# Opção B: Projeto existente (se já criou)
railway link
```

---

## 🚀 PASSO 4: Configurar Variáveis de Ambiente

### Método A: Via Dashboard (Recomendado)

1. Ir a https://railway.app/dashboard
2. Seleccionar projeto "aiti-assistant"
3. Clicar em "Settings"
4. Na seção "Environment", clicar "New Variable"
5. Adicionar cada variável:

```env
OPENAI_API_KEY=sk-proj-[SUA_CHAVE]
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=sqlite:////app/data/aiti.db
CHROMA_PERSIST_DIR=/app/data/vectorstore
COMPANY_NAME=TA Consulting Demo
COMPANY_LANGUAGE=pt-PT
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
```

### Método B: Via CLI

```bash
railway variables OPENAI_API_KEY sk-proj-[SUA_CHAVE]
railway variables LLM_MODEL gpt-4o-mini
# ... etc
```

---

## 🚀 PASSO 5: Deploy

```bash
railway up
```

**O que acontece:**
1. Build da aplicação (~2-3 minutos)
2. Deploy (~1-2 minutos)
3. App fica online automaticamente
4. URL gerada: `https://seu-app-xxxxx.railway.app`

**Verificar status:**
```bash
railway status
```

---

## ✅ PASSO 6: Validar Deploy

### 6.1 Teste Health Check

```bash
# Substituir com sua URL
curl https://seu-app-xxxxx.railway.app/api/health

# Resposta esperada:
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 6.2 Aceder à Documentação

- **Swagger UI:** https://seu-app-xxxxx.railway.app/docs
- **ReDoc:** https://seu-app-xxxxx.railway.app/redoc

### 6.3 Testar Chat

```bash
curl -X POST https://seu-app-xxxxx.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Qual é o horário de funcionamento?",
    "mode": "standard"
  }'
```

---

## 📚 PASSO 7: Ingerir FAQ (Dados de Demo)

### Via cURL (sem CLI access)

```bash
# Depois de fazer upload dos documentos
# (Ver seção "Upload de Documentos" abaixo)
```

### Via SSH no Container

```bash
# 1. Abrir shell no Railway
railway shell

# 2. Dentro do container
cd /app
python3 ingest_demo.py

# 3. Sair
exit
```

### Via API

```bash
# Ver endpoint POST /api/documents/upload na documentação
# https://seu-app-xxxxx.railway.app/docs
```

---

## 🎯 PASSO 8: Customizar para seu Caso de Uso

### Opção A: Adicionar Própria FAQ

1. Criar ficheiro `.txt` com sua FAQ
2. Upload via `/api/documents/upload`
3. Sistema indexa automaticamente em ~30 segundos

### Opção B: Modificar System Prompt

```bash
# Ir a Railway Dashboard → Variables
# Editar SYSTEM_PROMPT

# Exemplo para banco:
"Tu es un asistente especializado en servicios bancarios de [EMPRESA]. 
Respondes solo información sobre nuestros productos y servicios. 
Si no sabes, propone transferir con un especialista. Sé profesional y conciso."
```

### Opção C: Integrar em Website

```html
<!-- Copiar isto para seu website -->
<script src="https://seu-app-xxxxx.railway.app/widget/aiti-widget.js"></script>
<div id="aiti-widget"></div>
```

---

## 🔍 Monitoramento

### Logs em Tempo Real

```bash
railway logs
# Ou na dashboard: Logs tab
```

### Métricas

- Dashboard Railway mostra:
  - CPU/RAM usage
  - Networking
  - Requests/segunda
  - Error rates

### Alertas

Configuráveis na dashboard:
- Quando crash
- Quando memory > 80%
- Quando error rate > 5%

---

## 🚨 Troubleshooting

### "API key not configured"

```
Erro: ValueError: No LLM API key configured
Solução: Verificar que OPENAI_API_KEY ou ANTHROPIC_API_KEY está definida
         railway variables OPENAI_API_KEY sk-proj-...
```

### "Database connection failed"

```
Erro: sqlalchemy.exc.OperationalError
Solução: Verificar DATABASE_URL = sqlite:////app/data/aiti.db (4 slashes!)
```

### "Port already in use"

```
Erro: Address already in use
Solução: Railway atribui porta automaticamente via $PORT
         Não colocar port hardcoded no Procfile
```

### "Timeout na ingestão de documentos"

```
Erro: Request timeout
Solução: Reduzir tamanho do ficheiro
         Ou fazer upload em múltiplas partes
```

### "Resposta muito lenta"

```
Solução 1: Reduzir TOP_K_RESULTS (de 5 para 3)
Solução 2: Reduzir CHUNK_SIZE (de 500 para 300)
Solução 3: Usar modelo mais rápido (gpt-4o-mini é já muito rápido)
```

---

## 📊 Performance

### Latência Esperada

| Operação | Latência | Onde |
|----------|----------|------|
| Health check | <100ms | `/api/health` |
| Busca RAG | 1-2s | `/api/chat` |
| Upload doc | 5-30s | `/api/documents/upload` |
| Ingestão | ~30s | ingest_demo.py |

### Escalabilidade

- **Grátis:** ~500 queries/dia
- **Hobby ($5/mês):** ~2000 queries/dia
- **Pro ($12/mês):** ~10000 queries/dia
- **Team:** Unlimited

---

## 🔄 Updates & Rollback

### Fazer Nova Deploy

```bash
# Após fazer commit
git push origin main

# No Railway:
railway up
# Ou via dashboard → Redeploy
```

### Rollback para Versão Anterior

```bash
# Na dashboard:
# Deployments → Seleccionar deployment anterior → Rollback
```

---

## 🛑 Parar/Apagar Deploy

```bash
# Ver status
railway status

# Parar
railway stop

# Remover totalmente
railway remove
```

---

## 📞 Suporte

- **Documentação:** https://docs.railway.app
- **Status:** https://status.railway.app
- **Comunidade:** Discord Railway
- **Email:** support@railway.app

---

## 🎉 Próximos Passos (Pós-Deploy)

1. ✅ Teste a API em `/docs`
2. ✅ Ingerir FAQ português
3. ✅ Testar chat com perguntas reais
4. ✅ Configurar domínio customizado (opcional)
5. ✅ Integrar widget no seu website (opcional)
6. ✅ Setup alertas/monitoramento
7. ✅ Documentar para cliente

---

**Estimativa:** ~15 minutos para deployment completo  
**Última actualização:** 08 Fev 2026  
**Versão:** 1.0
