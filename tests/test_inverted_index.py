"""
Unit tests for PositionalInvertedIndex module.
"""
import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.inverted_index import PositionalInvertedIndex

def test_inverted_index_building():
    idx = PositionalInvertedIndex()
    corpus = {
        "D01": [("court", 0), ("order", 1), ("court", 2)],
        "D02": [("order", 0), ("passed", 1)]
    }
    idx.build_index(corpus)
    
    assert idx.total_docs == 2
    assert idx.get_document_frequency("court") == 1
    assert idx.get_document_frequency("order") == 2
    assert idx.get_term_frequency("court", "D01") == 2
    assert idx.get_postings("court")["D01"] == [0, 2]

def test_tfidf_calculation():
    idx = PositionalInvertedIndex()
    corpus = {
        "D01": [("bail", 0)],
        "D02": [("appeal", 0)]
    }
    idx.build_index(corpus)
    score = idx.compute_tfidf("bail", "D01")
    assert score > 0.0
    assert idx.compute_tfidf("bail", "D02") == 0.0
