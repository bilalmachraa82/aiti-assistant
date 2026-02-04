# Guia de Ingestão de Documentos

## Visão Geral

O AITI Assistant usa RAG (Retrieval-Augmented Generation) para responder com base nos documentos da sua empresa. Este guia explica como preparar e ingerir documentos.

---

## Formatos Suportados

| Formato | Extensão | Notas |
|---------|----------|-------|
| PDF | `.pdf` | Texto extraído automaticamente |
| Word | `.docx` | Preserva estrutura |
| Texto | `.txt`, `.md` | Processamento directo |
| CSV | `.csv` | Cada linha = 1 entrada |

---

## Estrutura Recomendada

Organize os documentos por categoria:

```
data/documents/
├── entregas/
│   ├── prazos-entrega.pdf
│   └── zonas-cobertura.txt
├── pagamentos/
│   ├── metodos-pagamento.pdf
│   └── parcelamento.txt
├── devolucoes/
│   └── politica-devolucoes.pdf
├── produtos/
│   ├── catalogo-2025.pdf
│   └── fichas-tecnicas/
│       ├── produto-a.txt
│       └── produto-b.txt
└── faq/
    └── perguntas-frequentes.docx
```

---

## Preparação dos Documentos

### Boas Práticas

1. **Use títulos claros** - Ajudam na busca
2. **Evite imagens de texto** - PDFs com texto seleccionável
3. **Separe por tema** - Um documento por tópico
4. **Mantenha actualizado** - Remova informação obsoleta

### Formato Ideal para FAQ

```markdown
## Qual o prazo de entrega?

O prazo de entrega para Portugal Continental é de 24 a 48 horas úteis.
Para as ilhas, o prazo é de 5 a 7 dias úteis.

## Posso devolver um produto?

Sim, tem 14 dias após a recepção para devolver qualquer produto,
sem necessidade de justificação. O produto deve estar na embalagem
original e sem sinais de uso.
```

### Formato para Produtos (CSV)

```csv
nome,descricao,preco,stock,categoria
Produto A,Descrição do produto A com especificações,29.90,150,Categoria 1
Produto B,Descrição do produto B com características,49.90,80,Categoria 2
```

---

## Comandos de Ingestão

### Ingerir Todos os Documentos

```bash
python -m app.ingest
```

### Com Output Detalhado

```bash
python -m app.ingest --verbose
```

### Ingerir Ficheiro Específico

```bash
python -m app.ingest --file data/documents/novo-documento.pdf
```

### Reiniciar Base (Limpar Tudo)

```bash
python -m app.ingest --reset
```

### Directório Personalizado

```bash
python -m app.ingest --dir /caminho/para/documentos
```

---

## Processo de Chunking

Os documentos são divididos em "chunks" para melhor busca:

```
Documento Original
        │
        ▼
┌───────────────────┐
│ Chunk 1 (500 chars)│
├───────────────────┤
│ Chunk 2 (500 chars)│◄── Overlap de 50 chars
├───────────────────┤
│ Chunk 3 (500 chars)│
└───────────────────┘
```

### Configurar Tamanho dos Chunks

No `.env`:
```env
CHUNK_SIZE=500      # Tamanho máximo de cada chunk
CHUNK_OVERLAP=50    # Sobreposição entre chunks
```

**Dicas:**
- Chunks menores = respostas mais precisas
- Chunks maiores = mais contexto
- Overlap ajuda a não cortar informação importante

---

## Verificar Ingestão

### Via API

```bash
curl http://localhost:8000/api/documents/stats
```

Resposta:
```json
{
  "total_documents": 15,
  "total_chunks": 234,
  "file_types": {
    ".pdf": 8,
    ".txt": 5,
    ".docx": 2
  }
}
```

### Testar Busca

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "prazo de entrega"}'
```

---

## Actualizar Documentos

### Adicionar Novo Documento

1. Copie o ficheiro para `data/documents/`
2. Execute:
```bash
python -m app.ingest --file data/documents/novo.pdf
```

### Remover Documento

```bash
curl -X DELETE http://localhost:8000/api/documents/{id}
```

### Actualizar Tudo

```bash
python -m app.ingest --reset
```

---

## Troubleshooting

### "No text extracted"
- Verifique se o PDF tem texto seleccionável (não é imagem)
- Tente converter para `.txt` primeiro

### Respostas imprecisas
- Divida documentos grandes em ficheiros menores
- Use títulos e secções claras
- Aumente `TOP_K_RESULTS` no `.env`

### Chunks duplicados
```bash
python -m app.ingest --reset
```

---

## Métricas de Qualidade

### Ideal
- Cada pergunta comum tem resposta na base
- Chunks contêm informação completa
- Nomes de ficheiros são descritivos

### Verificar Cobertura

Teste com perguntas comuns dos clientes:
1. Entregas e prazos
2. Pagamentos
3. Devoluções
4. Produtos específicos
5. Contactos e horários

Se alguma não tiver boa resposta, adicione documentação específica.
