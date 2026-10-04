"""
Unit tests for Evaluation and IR metrics.
"""
import pytest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils import calculate_precision_recall_f1, calculate_precision_recall_at_k

def test_metrics_standard():
    retrieved = ["D01", "D02", "D03", "D04"]
    relevant = ["D01", "D02", "D05"]
    p, r, f1 = calculate_precision_recall_f1(retrieved, relevant)
    # TP = 2 (D01, D02)
    # Precision = 2/4 = 0.5
    # Recall = 2/3 = 0.6667
    assert p == 0.5
    assert r == 0.6667
    assert f1 > 0.5

def test_metrics_zero_denominators():
    p, r, f1 = calculate_precision_recall_f1([], ["D01"])
    assert p == 0.0
    assert r == 0.0
    assert f1 == 0.0

    p2, r2, f1_2 = calculate_precision_recall_f1(["D01"], [])
    assert p2 == 0.0
    assert r2 == 0.0
    assert f1_2 == 0.0

def test_precision_recall_at_k():
    retrieved = ["D01", "D02", "D03", "D04", "D05", "D06"]
    relevant = ["D01", "D06"]
    p_k, r_k = calculate_precision_recall_at_k(retrieved, relevant, k=3)
    # At K=3, retrieved are [D01, D02, D03]. TP=1 (D01).
    # Precision@3 = 1/3 = 0.3333
    # Recall@3 = 1/2 = 0.5
    assert p_k == 0.3333
    assert r_k == 0.5
