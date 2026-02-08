# 🚀 Deployment Guide - AITI Assistant

## Railway (Recomendado)

Railway é ideal para FastAPI + ChromaDB porque oferece containers persistentes.

### Pré-requisitos
- Conta Railway: https://railway.app
- Git configurado

### Passos

1. **Fazer fork do repositório** (ou usar o seu próprio)
   ```bash
   git clone https://github.com/bilalmachraa82/aiti-assistant.git
   cd aiti-assistant
   ```

2. **Login no Railway**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

3. **Deploy**
   ```bash
   railway up
   ```

4. **Configurar variáveis de ambiente**
   - Aceder a: https://railway.app/project/seu-projeto
   - Clicar em "Settings"
   - Adicionar as seguintes variáveis:
     - `OPENAI_API_KEY`: sk-... (OpenAI API key)
     - `COMPANY_NAME`: Fernando Demo
     - `COMPANY_LANGUAGE`: pt-PT

5. **Ingerir documentos** (pós-deploy)
   ```bash
   # SSH no container Railway
   railway shell
   
   # Ou via HTTP direto na API
   curl -X POST https://seu-app.railway.app/api/documents/upload \
     -F "file=@seu-documento.pdf"
   ```

6. **Acessar**
   - API: `https://seu-app.railway.app`
   - Docs: `https://seu-app.railway.app/docs`
   - Demo: `https://seu-app.railway.app/demo`

---

## Vercel (Alternativo)

⚠️ Nota: Vercel é serverless, e ChromaDB funciona melhor com Railway. Use Vercel apenas se quiser arquitetura sem estado.

### Passos

1. Fazer fork do repositório

2. Conectar ao Vercel:
   - Ir a https://vercel.com
   - "New Project"
   - Seleccionar o repositório

3. Configurar ambiente:
   - Ambiente Python: 3.11
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0`

4. Adicionar variáveis de ambiente:
   - `OPENAI_API_KEY`
   - `COMPANY_NAME`

---

## Heroku (Legado)

```bash
heroku create seu-app
git push heroku main
heroku config:set OPENAI_API_KEY=sk-...
```

---

## Variáveis de Ambiente Essenciais

| Variável | Obrigatório | Descrição |
|----------|-------------|-----------|
| `OPENAI_API_KEY` | Sim* | API key OpenAI |
| `ANTHROPIC_API_KEY` | Sim* | API key Anthropic (alternativa) |
| `COMPANY_NAME` | Não | Nome da empresa (default: "Empresa") |
| `COMPANY_LANGUAGE` | Não | Idioma (default: pt-PT) |
| `LLM_MODEL` | Não | Modelo LLM (default: gpt-4o-mini) |
| `DATABASE_URL` | Não | URL da BD (default: SQLite local) |

*Uma das duas é obrigatória

---

## Domínio Customizado

Após deploy bem-sucedido:

1. Railway:
   - Ir a projeto → Settings
   - Custom Domain
   - Adicionar seu domínio

2. Vercel:
   - Projeto → Settings → Domains
   - Adicionar domínio

---

## Monitoramento

### Railway Dashboard
- Logs em tempo real
- Métricas de CPU/RAM
- Histórico de deployments

### API Health Check
```bash
curl https://seu-app.railway.app/api/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## Troubleshooting

### "API key not configured"
Verificar que a variável `OPENAI_API_KEY` ou `ANTHROPIC_API_KEY` está definida no Railway.

### "Database connection failed"
Railway já inclui persistência SQLite. Se usar BD externa, configurar `DATABASE_URL`.

### "Rate limit exceeded"
Verificar quota OpenAI em https://platform.openai.com/account/usage/overview

---

## Performance Tips

1. **Cache de embeddings**: ChromaDB já faz caching automático
2. **Modelo rápido**: Use `gpt-4o-mini` para menor latência
3. **Reduzir TOP_K_RESULTS**: Default 5, tentar 3 para mais rapidez
4. **Chunks menores**: CHUNK_SIZE default 500, pode reduzir para 300

---

## Rollback

### Railway
```bash
railway deploy --deployment [ID_ANTERIOR]
```

### Vercel
Vercel mantém histórico automático. Clicar em "Deployments" e reverter.

---

## Backup de Dados

### Dados ChromaDB
Railway guarda dados em `/app/data/vectorstore` persistentemente.

Para backup manual:
```bash
railway shell
tar -cz data/ > backup.tar.gz
exit
```

---

## Support

- 📧 Email: support@aiti.dev
- 📚 Docs: https://docs.aiti-assistant.dev
- 🐛 Issues: GitHub Issues
