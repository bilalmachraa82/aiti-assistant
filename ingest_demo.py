#!/usr/bin/env python3
"""
Script de ingestão de documentos de exemplo para AITI Assistant
Executa: python3 ingest_demo.py
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.rag.vectorstore import VectorStore


def ingest_demo_documents():
    """Ingerir documentos de demo."""
    print("\n" + "="*60)
    print("🤖 AITI Assistant - Ingestão de Documentos Demo")
    print("="*60 + "\n")
    
    # Inicializar vector store
    vectorstore = VectorStore()
    print("✅ Vector store inicializado")
    print(f"   Diretório: {settings.chroma_persist_dir}")
    
    # Ingerir FAQs de exemplo
    demo_dir = Path("data/demo")
    documents_to_ingest = [
        "faq-exemplo.txt",
        "faq-fernando.txt",
        "politicas.txt"
    ]
    
    total_chunks = 0
    for doc_file in documents_to_ingest:
        doc_path = demo_dir / doc_file
        if doc_path.exists():
            print(f"\n📄 Ingerindo: {doc_file}")
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Adicionar ao vector store
                chunks = vectorstore.add_documents(
                    documents=[{"content": text, "source": doc_file}],
                    metadatas=[{"source": doc_file}]
                )
                total_chunks += len(chunks)
                print(f"   ✅ {len(chunks)} chunks criados")
            except Exception as e:
                print(f"   ❌ Erro ao ingerir {doc_file}: {e}")
        else:
            print(f"\n⚠️  Ficheiro não encontrado: {doc_file}")
    
    print("\n" + "="*60)
    print(f"✅ Ingestão completa!")
    print(f"   Total de chunks: {total_chunks}")
    print(f"   Pronto para responder perguntas!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        ingest_demo_documents()
    except KeyboardInterrupt:
        print("\n⚠️  Ingestão cancelada")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
