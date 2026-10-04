"""
Utility functions for timing, text snippets, metrics calculation, and logging.
"""
import time
from contextlib import contextmanager
import re
from typing import List, Tuple, Dict, Any, Optional

@contextmanager
def timer():
    """Context manager to measure execution time in seconds."""
    start = time.perf_counter()
    result = {"elapsed_seconds": 0.0, "elapsed_ms": 0.0}
    try:
        yield result
    finally:
        elapsed = time.perf_counter() - start
        result["elapsed_seconds"] = elapsed
        result["elapsed_ms"] = elapsed * 1000.0

def generate_snippet(text: str, query_terms: List[str], max_chars: int = 300) -> str:
    """
    Extract a contextual snippet around occurrences of query terms in the text.
    Preserves readable sentence structure and highlights the matching region.
    """
    if not text:
        return ""
    if not query_terms:
        return text[:max_chars].strip() + ("..." if len(text) > max_chars else "")

    # Clean query terms of quotes and operators
    cleaned_terms = []
    for q in query_terms:
        q_clean = re.sub(r'["\']', '', q).strip()
        if q_clean and q_clean.upper() not in {"AND", "OR", "NOT"}:
            cleaned_terms.append(re.escape(q_clean))

    if not cleaned_terms:
        return text[:max_chars].strip() + ("..." if len(text) > max_chars else "")

    pattern = re.compile(r'\b(' + '|'.join(cleaned_terms) + r')\b', re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        # Fallback substring match if word boundary failed
        pattern_loose = re.compile('(' + '|'.join(cleaned_terms) + ')', re.IGNORECASE)
        match = pattern_loose.search(text)

    if not match:
        return text[:max_chars].strip() + ("..." if len(text) > max_chars else "")

    start_idx = max(0, match.start() - 100)
    end_idx = min(len(text), match.end() + 200)

    # Try to align to word boundaries
    while start_idx > 0 and not text[start_idx].isspace():
        start_idx -= 1
    while end_idx < len(text) and not text[end_idx].isspace():
        end_idx += 1

    prefix = "..." if start_idx > 0 else ""
    suffix = "..." if end_idx < len(text) else ""
    snippet = prefix + text[start_idx:end_idx].strip() + suffix
    # Normalize excessive newlines and whitespace
    snippet = re.sub(r'\s+', ' ', snippet)
    return snippet

def calculate_precision_recall_f1(retrieved: List[str], relevant: List[str]) -> Tuple[float, float, float]:
    """
    Calculate Precision, Recall, and F1 score with explicit handling of zero denominators.
    Convention: If retrieved is empty or relevant is empty, precision/recall default to 0.0.
    """
    retrieved_set = set(retrieved)
    relevant_set = set(relevant)
    
    tp = len(retrieved_set.intersection(relevant_set))
    fp = len(retrieved_set - relevant_set)
    fn = len(relevant_set - retrieved_set)

    precision = tp / len(retrieved_set) if retrieved_set else 0.0
    recall = tp / len(relevant_set) if relevant_set else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return round(precision, 4), round(recall, 4), round(f1, 4)

def calculate_precision_recall_at_k(retrieved: List[str], relevant: List[str], k: int = 5) -> Tuple[float, float]:
    """
    Calculate Precision@K and Recall@K cutoff metrics.
    """
    cutoff_retrieved = retrieved[:k]
    cutoff_set = set(cutoff_retrieved)
    relevant_set = set(relevant)

    tp_k = len(cutoff_set.intersection(relevant_set))
    precision_k = tp_k / min(k, len(cutoff_retrieved)) if cutoff_retrieved else 0.0
    recall_k = tp_k / len(relevant_set) if relevant_set else 0.0

    return round(precision_k, 4), round(recall_k, 4)
