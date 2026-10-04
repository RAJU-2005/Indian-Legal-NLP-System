"""
Unit tests for tokenizers module.
"""
import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.tokenizers import (
    NLTKTokenizer, SpacyTokenizer, CustomLegalTokenizer, HybridTokenizer
)

def test_nltk_tokenizer():
    tok = NLTKTokenizer()
    tokens = tok.tokenize("The appellant filed bail.")
    assert "appellant" in tokens
    assert "bail" in tokens

def test_spacy_tokenizer():
    tok = SpacyTokenizer()
    tokens = tok.tokenize("Section 302 of IPC was applied.")
    assert len(tokens) >= 5

def test_custom_legal_tokenizer_section_preservation():
    tok = CustomLegalTokenizer()
    tokens = tok.tokenize("The accused was charged under Section 302 IPC and Article 21.")
    assert any("Section 302" in t for t in tokens)
    assert any("Article 21" in t for t in tokens)

def test_custom_legal_tokenizer_currency():
    tok = CustomLegalTokenizer()
    tokens = tok.tokenize("Bail granted on ₹50,000 bond.")
    assert "₹50,000" in tokens

def test_custom_legal_tokenizer_latin_maxim():
    tok = CustomLegalTokenizer()
    tokens = tok.tokenize("The court took suo motu cognizance.")
    assert any("suo motu" in t for t in tokens)
