"""
AITI Assistant - Document Ingestion
Processes documents and creates embeddings for the RAG pipeline.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import structlog

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.config import settings
from app.rag.vectorstore import VectorStore

logger = structlog.get_logger()


# Document processing functions
def load_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Load and extract text from PDF file."""
    try:
        from PyPDF2 import PdfReader
        
        reader = PdfReader(file_path)
        chunks = []
        
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text and text.strip():
                chunks.append({
                    "text": text.strip(),
                    "metadata": {
                        "source": os.path.basename(file_path),
                        "page": page_num,
                        "type": "pdf"
                    }
                })
        
        return chunks
    except Exception as e:
        logger.error("Failed to load PDF", file=file_path, error=str(e))
        return []


def load_docx(file_path: str) -> List[Dict[str, Any]]:
    """Load and extract text from DOCX file."""
    try:
        from docx import Document
        
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        
        if text:
            return [{
                "text": text,
                "metadata": {
                    "source": os.path.basename(file_path),
                    "type": "docx"
                }
            }]
        return []
    except Exception as e:
        logger.error("Failed to load DOCX", file=file_path, error=str(e))
        return []


def load_text(file_path: str) -> List[Dict[str, Any]]:
    """Load text file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        
        if text:
            return [{
                "text": text,
                "metadata": {
                    "source": os.path.basename(file_path),
                    "type": "text"
                }
            }]
        return []
    except Exception as e:
        logger.error("Failed to load text file", file=file_path, error=str(e))
        return []


def load_csv(file_path: str) -> List[Dict[str, Any]]:
    """Load CSV file - each row becomes a chunk."""
    try:
        import csv
        
        chunks = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, 1):
                # Convert row to text
                text = " | ".join([f"{k}: {v}" for k, v in row.items() if v])
                if text:
                    chunks.append({
                        "text": text,
                        "metadata": {
                            "source": os.path.basename(file_path),
                            "row": row_num,
                            "type": "csv"
                        }
                    })
        
        return chunks
    except Exception as e:
        logger.error("Failed to load CSV", file=file_path, error=str(e))
        return []


def load_document(file_path: str) -> List[Dict[str, Any]]:
    """Load document based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    
    loaders = {
        ".pdf": load_pdf,
        ".docx": load_docx,
        ".txt": load_text,
        ".md": load_text,
        ".csv": load_csv
    }
    
    loader = loaders.get(ext)
    if loader:
        return loader(file_path)
    else:
        logger.warning("Unsupported file type", file=file_path, extension=ext)
        return []


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Split text into chunks with overlap.
    
    Args:
        text: The text to split
        chunk_size: Maximum chunk size in characters
        overlap: Number of characters to overlap between chunks
    """
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence ending
            for sep in [". ", ".\n", "? ", "!\n"]:
                last_sep = text[start:end].rfind(sep)
                if last_sep > chunk_size * 0.5:  # At least halfway
                    end = start + last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start < 0:
            start = 0
    
    return chunks


def process_documents(documents_dir: str, vectorstore: VectorStore, verbose: bool = False):
    """
    Process all documents in directory and add to vectorstore.
    
    Args:
        documents_dir: Directory containing documents
        vectorstore: VectorStore instance
        verbose: Print detailed progress
    """
    documents_path = Path(documents_dir)
    
    if not documents_path.exists():
        logger.error("Documents directory not found", path=documents_dir)
        return
    
    # Find all supported files
    extensions = ["*.pdf", "*.docx", "*.txt", "*.md", "*.csv"]
    files = []
    for ext in extensions:
        files.extend(documents_path.rglob(ext))
    
    if not files:
        logger.warning("No documents found", path=documents_dir)
        return
    
    logger.info("Found documents to process", count=len(files))
    
    all_texts = []
    all_metadatas = []
    
    for file_path in files:
        if verbose:
            print(f"Processing: {file_path.name}")
        
        # Load document
        doc_chunks = load_document(str(file_path))
        
        for doc in doc_chunks:
            # Split into smaller chunks
            text_chunks = chunk_text(doc["text"])
            
            for i, chunk in enumerate(text_chunks):
                all_texts.append(chunk)
                metadata = doc["metadata"].copy()
                metadata["chunk_index"] = i
                all_metadatas.append(metadata)
        
        if verbose:
            print(f"  → {len(doc_chunks)} pages/sections, chunked")
    
    # Add to vectorstore
    if all_texts:
        logger.info("Adding chunks to vectorstore", count=len(all_texts))
        vectorstore.add_documents(all_texts, all_metadatas)
        logger.info("Ingestion complete", total_chunks=len(all_texts))
    else:
        logger.warning("No text extracted from documents")


def main():
    """Main entry point for ingestion."""
    parser = argparse.ArgumentParser(description="AITI Assistant - Document Ingestion")
    parser.add_argument("--file", type=str, help="Process specific file instead of directory")
    parser.add_argument("--reset", action="store_true", help="Clear vectorstore before ingestion")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--dir", type=str, default="data/documents", help="Documents directory")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("🤖 AITI Assistant - Document Ingestion")
    print("=" * 50)
    
    # Initialize vectorstore
    vectorstore = VectorStore()
    
    # Reset if requested
    if args.reset:
        print("🗑️  Clearing existing vectorstore...")
        vectorstore.clear()
    
    # Process documents
    if args.file:
        print(f"📄 Processing single file: {args.file}")
        doc_chunks = load_document(args.file)
        
        all_texts = []
        all_metadatas = []
        
        for doc in doc_chunks:
            text_chunks = chunk_text(doc["text"])
            for i, chunk in enumerate(text_chunks):
                all_texts.append(chunk)
                metadata = doc["metadata"].copy()
                metadata["chunk_index"] = i
                all_metadatas.append(metadata)
        
        if all_texts:
            vectorstore.add_documents(all_texts, all_metadatas)
            print(f"✅ Added {len(all_texts)} chunks")
        else:
            print("⚠️  No text extracted from file")
    else:
        print(f"📁 Processing directory: {args.dir}")
        process_documents(args.dir, vectorstore, verbose=args.verbose)
    
    # Print stats
    stats = vectorstore.get_stats()
    print("=" * 50)
    print(f"✅ Ingestion complete!")
    print(f"   Total chunks in vectorstore: {stats['document_count']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
