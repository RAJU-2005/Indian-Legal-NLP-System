"""
Positional Inverted Index module for Legal Judgment Retrieval.
Builds and maintains positional postings: term -> {doc_id: [positions]}.
Supports JSON serialization and TF-IDF calculation for ranked retrieval.
"""
from typing import Dict, List, Set, Any, Optional, Tuple
from pathlib import Path
import json
import math
from collections import defaultdict

try:
    from config import INVERTED_INDEX_JSON
except ImportError:
    from ..config import INVERTED_INDEX_JSON

class PositionalInvertedIndex:
    """Positional Inverted Index with document postings and positional offsets."""

    def __init__(self):
        # index structure: {term: {doc_id: [pos1, pos2, ...]}}
        self.index: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))
        self.doc_lengths: Dict[str, int] = {}
        self.total_docs: int = 0
        self.doc_ids: List[str] = []

    def build_index(self, processed_corpus: Dict[str, List[Tuple[str, int]]]):
        """
        Build positional index from corpus of (token, position) pairs.
        """
        self.index.clear()
        self.doc_lengths.clear()
        self.doc_ids = sorted(list(processed_corpus.keys()))
        self.total_docs = len(self.doc_ids)

        for doc_id, token_pos_list in processed_corpus.items():
            self.doc_lengths[doc_id] = len(token_pos_list)
            for token, pos in token_pos_list:
                if token:
                    self.index[token][doc_id].append(pos)

    def get_postings(self, term: str) -> Dict[str, List[int]]:
        """Return positional postings dictionary for a term: {doc_id: [positions]}."""
        return self.index.get(term, {})

    def get_doc_set(self, term: str) -> Set[str]:
        """Return the set of document IDs containing term."""
        return set(self.index.get(term, {}).keys())

    def get_document_frequency(self, term: str) -> int:
        """Return number of documents containing term."""
        return len(self.index.get(term, {}))

    def get_term_frequency(self, term: str, doc_id: str) -> int:
        """Return occurrence count of term within a specific document."""
        return len(self.index.get(term, {}).get(doc_id, []))

    def compute_tfidf(self, term: str, doc_id: str) -> float:
        """
        Calculate TF-IDF score for term in doc_id using smooth IDF:
        TF = 1 + log10(tf) if tf > 0 else 0
        IDF = log10(1 + N / (1 + df))
        """
        tf = self.get_term_frequency(term, doc_id)
        if tf == 0:
            return 0.0
        df = self.get_document_frequency(term)
        idf = math.log10(1.0 + (self.total_docs / (1.0 + df)))
        return (1.0 + math.log10(tf)) * idf

    def export_json(self, output_path: Optional[Path] = None) -> Path:
        """Export index to JSON file."""
        out = output_path or INVERTED_INDEX_JSON
        # Convert defaultdicts to regular dicts for json serialization
        serializable_index = {
            term: dict(doc_postings) for term, doc_postings in self.index.items()
        }
        data = {
            "total_documents": self.total_docs,
            "vocabulary_size": len(self.index),
            "doc_ids": self.doc_ids,
            "doc_lengths": self.doc_lengths,
            "index": serializable_index
        }
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return out
