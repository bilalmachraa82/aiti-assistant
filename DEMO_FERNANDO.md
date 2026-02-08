# 🎯 Demo AITI Assistant para Fernando

## ⚡ Quick Start (3 minutos)

### Opção 1: Testar Localmente

```bash
# 1. Clone
git clone https://github.com/bilalmachraa82/aiti-assistant.git
cd aiti-assistant

# 2. Setup
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar
cp .env.example .env
# Edite .env e adicione sua OPENAI_API_KEY

# 4. Executar
uvicorn app.main:app --reload --port 8000

# 5. Acessar
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Demo: http://localhost:8000/demo
```

### Opção 2: Deploy no Railway (Recomendado - 5 minutos)

**URL Final:** `https://aiti-assistant-fernando.railway.app`

#### Passo-a-Passo:

1. **Fazer Fork** do repositório
   - https://github.com/bilalmachraa82/aiti-assistant
   - Clicar "Fork" → "Create fork"

2. **Conectar ao Railway**
   - Ir a https://railway.app
   - Clicar "New Project"
   - "Deploy from GitHub"
   - Seleccionar o fork

3. **Configurar Variáveis** (crítico!)
   - Projeto → Settings
   - Variables
   - Adicionar:
     ```
     OPENAI_API_KEY=sk-proj-YourKeyHere
     COMPANY_NAME=Fernando
     COMPANY_LANGUAGE=pt-PT
     ```

4. **Deploy Automático**
   - Railway faz deploy automaticamente
   - Aguardar 2-3 minutos
   - URL será: `https://[seu-app-name].railway.app`

5. **Testar**
   - Abrir em navegador: `https://seu-app.railway.app/docs`
   - Testar endpoint `/api/health`

---

## 🧪 Testes Rápidos

### Teste 1: Health Check
```bash
curl https://seu-app.railway.app/api/health | jq .
```

**Resposta esperada:** Status `healthy`, vectorstore `0 documents`

### Teste 2: Chat (sem documentos indexados)
```bash
curl -X POST https://seu-app.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Qual o prazo de entrega?",
    "mode": "standard"
  }'
```

**Resposta:** Sistema dirá que não tem informação. Isso é esperado até ingerir documentos.

### Teste 3: Ingerir Documentos (FAQ de exemplo)
```bash
# Se no servidor local:
python3 ingest_demo.py

# Se no Railway, fazer upload via API:
curl -X POST https://seu-app.railway.app/api/documents/upload \
  -F "file=@data/demo/faq-exemplo.txt"
```

### Teste 4: Chat (com documentos)
Após ingerir, fazer novamente o teste 2. Agora responderá com informação do FAQ!

---

## 📊 Demo Features

### Documentos Inclusos (Portuguese)

Já estão na pasta `data/demo/`:
- `faq-exemplo.txt` - FAQ de e-commerce
- `faq-fernando.txt` - FAQ específica para esta demo
- `politicas.txt` - Políticas de empresa

### Perguntas para Testar

Após ingerir documentos, tente:

```
1. "Qual o prazo de entrega para Lisboa?"
   → Deve responder: "24 a 48 horas úteis"

2. "Quanto custa entrega?"
   → Deve responder: "4,90€ até 50€, grátis acima"

3. "Como faço devolução?"
   → Deve detalhar o processo

4. "Qual seu horário de atendimento?"
   → Deve responder: "Seg-Sex 9h-18h"

5. "O que é AITI Assistant?"
   → Deve explicar com base no FAQ do Fernando
```

---

## 🎨 Exemplos de Integração

### Website Widget
```html
<script src="https://seu-app.railway.app/widget/aiti-widget.js"></script>
<script>
  AITIWidget.init({
    apiUrl: 'https://seu-app.railway.app',
    position: 'bottom-right'
  });
</script>
```

### Python/Node.js

```python
import requests

response = requests.post('https://seu-app.railway.app/api/chat', json={
  'query': 'Como funciono?',
  'mode': 'standard'
})
print(response.json())
```

---

## 📈 Métricas

Após alguns testes, verificar:

```bash
# Listar documentos indexados
curl https://seu-app.railway.app/api/documents

# Ver métricas (quando implementado)
curl https://seu-app.railway.app/api/metrics
```

---

## 🚨 Troubleshooting

### "Invalid API Key"
- Verificar que `OPENAI_API_KEY` está correct em Railway
- Confirmar que a chave começa com `sk-`

### "Vectorstore not initialized"
- Aguardar 30 segundos após deploy
- Fazer refresh na página

### "No documents indexed"
- Normal! Executar `python3 ingest_demo.py`
- Ou fazer upload via `/api/documents/upload`

### "Responses are generic"
- Adicionar mais documentos (o RAG melhora com mais dados)
- Aumentar `TOP_K_RESULTS` de 5 para 10

---

## 📞 Próximos Passos

1. ✅ **Deploy completo** (feito acima)
2. ⏭️  **Adicionar seus documentos** (PDFs, FAQs, políticas)
3. ⏭️  **Testar com perguntas reais** (sobre seu negócio)
4. ⏭️  **Integrar widget no website** (2 linhas de código)
5. ⏭️  **Monitorar uso** (Dashboard em Railway)

---

## 🎁 Bónus: Customizações

### Mudar "Personalidade"
Editar em `.env`:
```
SYSTEM_PROMPT="Você é um assistente amigável e profissional da {company}..."
```

### Multi-idiomas
```
COMPANY_LANGUAGE=es  # Espanhol
COMPANY_LANGUAGE=fr  # Francês
COMPANY_LANGUAGE=en  # Inglês
```

### Modelo mais rápido
```
LLM_MODEL=gpt-3.5-turbo  # Mais rápido, menos preciso
```

### Modelo mais preciso
```
LLM_MODEL=gpt-4  # Mais preciso, mais lento
```

---

## 📞 Suporte

- 📧 **Email**: support@aiti.dev
- 🔗 **Docs**: https://docs.aiti-assistant.dev
- 🐛 **GitHub**: https://github.com/bilalmachraa82/aiti-assistant

---

## ✨ Conclusão

O **AITI Assistant** está pronto! Podes:

✅ Responder automaticamente às FAQs
✅ Funcionar 24/7 sem custos humanos
✅ Escalar quando necessário
✅ Integrar em qualquer lugar

**Que destaques demais?**

Comenta em baixo ou contacta-nos! 🚀
