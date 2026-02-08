#!/usr/bin/env python3
"""
Script de teste para a API AITI Assistant
Executa: python3 test_api.py
"""

import os
import sys
import asyncio
from pathlib import Path
from httpx import AsyncClient

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app
from app.config import settings


async def test_api():
    """Testar endpoints da API."""
    print("\n" + "="*60)
    print("🧪 AITI Assistant - Teste da API")
    print("="*60 + "\n")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Testar endpoint root
        print("1️⃣  Testando GET /")
        response = await client.get("/")
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.json()}")
        
        # 2. Testar health check
        print("\n2️⃣  Testando GET /api/health")
        response = await client.get("/api/health")
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.json()}")
        
        # 3. Testar chat (sem documentos indexados)
        print("\n3️⃣  Testando POST /api/chat (sem documentos)")
        query_data = {
            "query": "Qual é o seu horário de funcionamento?",
            "mode": "standard"
        }
        try:
            response = await client.post("/api/chat", json=query_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Resposta: {response.json()}")
            else:
                print(f"   Erro: {response.text}")
        except Exception as e:
            print(f"   ⚠️  Esperado - sem API key configurada: {e}")
        
        # 4. Testar documents upload
        print("\n4️⃣  Testando GET /api/documents")
        response = await client.get("/api/documents")
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.json()}")
    
    print("\n" + "="*60)
    print("✅ Testes completos!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(test_api())
    except KeyboardInterrupt:
        print("\n⚠️  Teste cancelado")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
