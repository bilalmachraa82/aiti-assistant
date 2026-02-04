# Guia de Instalação - AITI Assistant

## Requisitos

### Sistema
- Python 3.11 ou superior
- 2GB RAM mínimo (4GB recomendado)
- 1GB espaço em disco

### API Keys
Precisa de uma das seguintes:
- **OpenAI API Key** (recomendado) - [Obter aqui](https://platform.openai.com/)
- **Anthropic API Key** (alternativa) - [Obter aqui](https://console.anthropic.com/)

---

## Instalação Local

### 1. Clonar o Repositório

```bash
git clone https://github.com/bilalmachraa82/aiti-assistant.git
cd aiti-assistant
```

### 2. Criar Ambiente Virtual

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite o ficheiro `.env`:

```env
# Obrigatório - escolha um
OPENAI_API_KEY=sk-sua-chave-openai

# Informação da empresa
COMPANY_NAME=Nome da Sua Empresa

# Opcional - Bot Telegram
TELEGRAM_BOT_TOKEN=123456:ABC...
```

### 5. Ingerir Documentos de Demo

```bash
# Copiar documentos de exemplo
cp -r data/demo/* data/documents/

# Executar ingestão
python -m app.ingest --verbose
```

### 6. Iniciar o Servidor

```bash
uvicorn app.main:app --reload --port 8000
```

### 7. Testar

Abra o browser em:
- Demo: http://localhost:8000/demo
- API Docs: http://localhost:8000/docs

---

## Instalação com Docker

### 1. Construir a Imagem

```bash
docker build -t aiti-assistant .
```

### 2. Executar

```bash
docker run -d \
  --name aiti-assistant \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-sua-chave \
  -e COMPANY_NAME="Sua Empresa" \
  -v $(pwd)/data:/app/data \
  aiti-assistant
```

### Com Docker Compose

```bash
# Criar ficheiro .env com as variáveis
docker-compose up -d

# Com bot Telegram
docker-compose --profile telegram up -d
```

---

## Configuração de Produção

### Variáveis Recomendadas

```env
# Produção
DEBUG=false
LOG_LEVEL=INFO

# Segurança
API_KEY=sua-chave-api-secreta
CORS_ORIGINS=https://seusite.pt

# Performance
CHUNK_SIZE=500
TOP_K_RESULTS=5
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.seusite.pt;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Systemd Service

```ini
[Unit]
Description=AITI Assistant API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/aiti-assistant
ExecStart=/opt/aiti-assistant/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Troubleshooting

### Erro: "No LLM API key configured"
Verifique se `OPENAI_API_KEY` ou `ANTHROPIC_API_KEY` está definido no `.env`.

### Erro: "chromadb" import
```bash
pip install chromadb --upgrade
```

### Servidor não inicia
Verifique se a porta 8000 está livre:
```bash
lsof -i :8000
```

### Documentos não são encontrados
Verifique se executou a ingestão:
```bash
python -m app.ingest --verbose
```

---

## Próximos Passos

1. [Configurar documentos](INGESTION.md)
2. [Integrar widget no website](WIDGET.md)
3. [Configurar bot Telegram](API.md#telegram)
