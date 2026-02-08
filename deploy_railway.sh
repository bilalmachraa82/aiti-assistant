#!/bin/bash
# 🚀 Script de deployment automático no Railway
# Uso: ./deploy_railway.sh

set -e

echo "🚀 AITI Assistant - Deploy para Railway"
echo "========================================"

# 1. Verificar se Railway CLI está instalado
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI não encontrado!"
    echo "   Instale com: npm install -g @railway/cli"
    exit 1
fi

# 2. Verificar se está no diretório correto
if [ ! -f "app/main.py" ]; then
    echo "❌ Deve executar este script no diretório raiz do projeto"
    exit 1
fi

# 3. Fazer login
echo "📧 Fazer login no Railway..."
railway login

# 4. Criar projeto (ou usar existente)
echo "📦 Criando projeto no Railway..."
railway init

# 5. Configurar variáveis de ambiente
echo "🔐 Configurar variáveis de ambiente?"
echo "   Adicione em: railway project settings"
echo ""
echo "   Variáveis obrigatórias:"
echo "   - OPENAI_API_KEY ou ANTHROPIC_API_KEY"
echo "   - COMPANY_NAME (opcional)"
echo ""
read -p "   Pressione Enter para continuar..."

# 6. Fazer deploy
echo "🚀 Iniciando deploy..."
railway up

# 7. Obter URL
echo ""
echo "✅ Deploy concluído!"
echo ""
echo "📌 URL do seu app:"
railway open

echo ""
echo "📚 Próximos passos:"
echo "   1. Configure as variáveis de ambiente"
echo "   2. Ingira seus documentos: python3 ingest_demo.py"
echo "   3. Teste em: https://seu-app.railway.app/docs"
echo ""
