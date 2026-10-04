"""
Unit tests for QueryProcessor module.
"""
import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.inverted_index import PositionalInvertedIndex
from src.query_processor import QueryProcessor

@pytest.fixture
def mock_index():
    idx = PositionalInvertedIndex()
    # Mock documents:
    # D01: ["bail", "application", "accused"]
    # D02: ["anticipatory", "bail", "appeal"]
    # D03: ["criminal", "appeal", "murder"]
    corpus = {
        "D01": [("bail", 0), ("application", 1), ("accused", 2)],
        "D02": [("anticipatori", 0), ("bail", 1), ("appeal", 2)],
        "D03": [("crimin", 0), ("appeal", 1), ("murder", 2)]
    }
    idx.build_index(corpus)
    return idx

def test_single_term_lookup(mock_index):
    qp = QueryProcessor(mock_index, lambda w: w.lower())
    res = qp.execute_boolean_query("bail")
    assert res == {"D01", "D02"}

def test_boolean_and(mock_index):
    qp = QueryProcessor(mock_index, lambda w: w.lower())
    res = qp.execute_boolean_query("bail AND appeal")
    assert res == {"D02"}

def test_boolean_or(mock_index):
    qp = QueryProcessor(mock_index, lambda w: w.lower())
    res = qp.execute_boolean_query("bail OR murder")
    assert res == {"D01", "D02", "D03"}

def test_boolean_not(mock_index):
    qp = QueryProcessor(mock_index, lambda w: w.lower())
    res = qp.execute_boolean_query("bail AND NOT appeal")
    assert res == {"D01"}

def test_phrase_query(mock_index):
    qp = QueryProcessor(mock_index, lambda w: w.lower())
    # Phrase "crimin appeal" should match D03 because pos 0 and 1 are adjacent
    res = qp.search_phrase('"crimin appeal"')
    assert res == {"D03"}
