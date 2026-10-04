"""
Retrieval engine for Indian Legal Judgment System.
Coordinates Boolean, Phrase, and TF-IDF Ranked search over PositionalInvertedIndex,
extracts contextual text snippets, and computes response execution times.
"""
from typing import List, Dict, Any, Tuple, Optional, Set
import math
from pathlib import Path
import pandas as pd

try:
    from src.query_processor import QueryProcessor
    from src.utils import timer, generate_snippet
    from config import RETRIEVAL_RESULTS_CSV
except ImportError:
    from .query_processor import QueryProcessor
    from .utils import timer, generate_snippet
    from ..config import RETRIEVAL_RESULTS_CSV

class LegalRetrievalEngine:
    """End-to-end information retrieval engine supporting Boolean and Ranked queries."""

    def __init__(self, index, raw_documents: Dict[str, Dict[str, Any]], normalizer_func):
        self.index = index
        self.documents = raw_documents
        self.normalizer = normalizer_func
        self.query_processor = QueryProcessor(index, normalizer_func)

    def search(self, query: str, query_type: str = "auto") -> Dict[str, Any]:
        """
        Execute search query and return formatted results with snippets and timing.
        Query types: 'keyword', 'phrase', 'boolean', 'ranked', 'auto'
        """
        q = query.strip()
        matched_doc_ids: List[str] = []
        scores: Dict[str, float] = {}

        # Determine effective query type if 'auto'
        eff_type = query_type.lower()
        if eff_type == "auto":
            if any(op in q for op in [" AND ", " OR ", " NOT "]) or q.startswith("NOT "):
                eff_type = "boolean"
            elif (q.startswith('"') and q.endswith('"')) or (q.startswith("'") and q.endswith("'")):
                eff_type = "phrase"
            elif len(q.split()) > 1:
                eff_type = "ranked"
            else:
                eff_type = "keyword"

        with timer() as t:
            if eff_type in {"keyword", "phrase", "boolean"}:
                doc_set = self.query_processor.execute_boolean_query(q)
                matched_doc_ids = sorted(list(doc_set))
                # For unranked boolean matches, score = 1.0
                scores = {doc_id: 1.0 for doc_id in matched_doc_ids}
            elif eff_type == "ranked":
                # TF-IDF Cosine Similarity Ranking
                matched_doc_ids, scores = self.rank_tfidf(q)

        # Extract snippet words
        query_words = [w.strip('"\'') for w in q.split() if w.upper() not in {"AND", "OR", "NOT"}]

        results = []
        for doc_id in matched_doc_ids:
            doc_info = self.documents.get(doc_id, {})
            cleaned_text = doc_info.get("cleaned_text", "")
            snippet = generate_snippet(cleaned_text, query_words)

            results.append({
                "document_id": doc_id,
                "score": round(scores.get(doc_id, 0.0), 4),
                "case_name": doc_info.get("case_name", "N/A"),
                "court_year": doc_info.get("court_year", "N/A"),
                "sector": doc_info.get("sector", "N/A"),
                "key_law": doc_info.get("key_law", "N/A"),
                "snippet": snippet
            })

        return {
            "query": query,
            "query_type": eff_type,
            "execution_time_ms": round(t["elapsed_ms"], 2),
            "num_results": len(results),
            "results": results
        }

    def rank_tfidf(self, query: str) -> Tuple[List[str], Dict[str, float]]:
        """
        Rank documents using TF-IDF vector space model with Cosine Similarity.
        """
        raw_words = query.strip('"\'').split()
        norm_words = [self.normalizer(w) for w in raw_words if w.strip()]
        
        # Calculate Query Vector weights
        query_weights = {}
        for w in norm_words:
            df = self.index.get_document_frequency(w)
            if df > 0:
                idf = math.log10(1.0 + (self.index.total_docs / (1.0 + df)))
                query_weights[w] = (1.0 + math.log10(norm_words.count(w))) * idf

        if not query_weights:
            return [], {}

        q_norm = math.sqrt(sum(v**2 for v in query_weights.values()))
        if q_norm == 0:
            return [], {}

        # Candidate documents containing at least one query term
        candidate_docs = set()
        for w in query_weights.keys():
            candidate_docs.update(self.index.get_doc_set(w))

        scores = {}
        for doc_id in candidate_docs:
            doc_len = self.index.doc_lengths.get(doc_id, 1)
            dot_product = 0.0
            doc_vec_sq = 0.0
            
            for w, q_wt in query_weights.items():
                d_wt = self.index.compute_tfidf(w, doc_id)
                dot_product += q_wt * d_wt
                doc_vec_sq += d_wt**2

            if doc_vec_sq > 0:
                cosine_sim = dot_product / (q_norm * math.sqrt(doc_vec_sq))
                scores[doc_id] = cosine_sim

        # Sort descending by score
        ranked_doc_ids = sorted(scores.keys(), key=lambda d: scores[d], reverse=True)
        return ranked_doc_ids, scores
