"""
Unit tests for DocumentLoader module.
"""
import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.document_loader import DocumentLoader

def test_document_loader_initialization():
    loader = DocumentLoader()
    assert loader is not None
    assert loader.dataset_dir.is_dir()

def test_clean_text_conservative():
    loader = DocumentLoader()
    raw = "The high court has juris-\ndiction under \x0c Section 302."
    cleaned = loader.clean_text_conservative(raw)
    assert "jurisdiction" in cleaned
    assert "\x0c" not in cleaned
    assert "Section 302" in cleaned

def test_load_documents_count_and_keys():
    loader = DocumentLoader()
    docs = loader.load_documents()
    assert len(docs) >= 15, "Corpus must meet minimum of 15 documents"
    assert "D01" in docs
    doc1 = docs["D01"]
    assert "cleaned_text" in doc1
    assert "token_count" in doc1
    assert doc1["token_count"] > 0
