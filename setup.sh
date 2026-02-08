#!/bin/bash
# Setup script para AITI Assistant no Railway

set -e

echo "🚀 AITI Assistant - Setup para Railway"
echo "========================================"

# 1. Instalar dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --quiet

# 2. Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p data/vectorstore
mkdir -p data/documents
mkdir -p logs

# 3. Verificar se há documentos a ingerir
echo "📄 Configurando documentos..."
if [ -f "ingest_demo.py" ]; then
    echo "   ℹ️  Para ingerir documentos de demo, execute: python3 ingest_demo.py"
fi

# 4. Configurar arquivo de status
echo "✅ Setup completo!"
echo "========================================"
echo ""
echo "Próximos passos:"
echo "1. Configure as variáveis de ambiente (Railway → Settings)"
echo "2. Execute: python3 ingest_demo.py (opcional, para dados de demo)"
echo "3. A API iniciará automaticamente em http://localhost:\$PORT"
echo ""
