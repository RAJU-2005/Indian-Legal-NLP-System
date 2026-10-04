"""
Query Processor module for Indian Legal Judgment Retrieval System.
Provides safe tokenization, operator parsing, phrase extraction, and AST evaluation
for Keyword, Phrase, Boolean (AND, OR, NOT), and Ranked queries without unsafe eval().
"""
from typing import List, Set, Dict, Any, Tuple, Optional
import re

class QueryProcessor:
    """Parses and executes Boolean and phrase queries over PositionalInvertedIndex."""

    def __init__(self, index, normalizer_func):
        self.index = index
        self.normalizer = normalizer_func

    def search_term(self, term: str) -> Set[str]:
        """
        Lookup single term in index.
        Supports exact match, raw lower match, and prefix/morphological expansion
        (e.g., 'smuggl' -> matches 'smuggling', 'smuggled').
        """
        clean_term = term.strip('"\'').strip()
        if not clean_term:
            return set()
        norm_term = self.normalizer(clean_term)
        exact_matches = self.index.get_doc_set(norm_term)
        if exact_matches:
            return exact_matches

        raw_lower = clean_term.lower()
        if raw_lower in self.index.index:
            return self.index.get_doc_set(raw_lower)

        # Prefix and morphological expansion if exact term not found
        if len(raw_lower) >= 3:
            prefix_matches = set()
            for indexed_term in self.index.index.keys():
                if indexed_term.startswith(raw_lower) or (len(raw_lower) >= 5 and raw_lower.startswith(indexed_term)):
                    prefix_matches.update(self.index.get_doc_set(indexed_term))
            if prefix_matches:
                return prefix_matches

        return set()

    def search_phrase(self, phrase: str) -> Set[str]:
        """
        Positional and unified phrase search:
        1. Checks for unified domain token match in index (e.g. 'section 302', 'habeas corpus').
        2. Checks if consecutive phrase terms appear at adjacent positions within the same document.
        """
        clean_phrase = phrase.strip('"\'').strip()
        if not clean_phrase:
            return set()

        # Step 1: Check if full phrase exists directly as a unified domain token
        norm_phrase = clean_phrase.lower()
        if norm_phrase in self.index.index:
            return self.index.get_doc_set(norm_phrase)

        matching_docs = set()

        # Step 2: Check positional adjacency of constituent words
        raw_words = clean_phrase.split()
        norm_words = [self.normalizer(w) for w in raw_words if w.strip()]
        if not norm_words:
            return matching_docs

        if len(norm_words) == 1:
            matching_docs.update(self.search_term(norm_words[0]))
            return matching_docs

        doc_candidates = self.search_term(norm_words[0])
        for w in norm_words[1:]:
            doc_candidates = doc_candidates.intersection(self.search_term(w))

        for doc_id in doc_candidates:
            first_positions = self.index.get_postings(norm_words[0]).get(doc_id, [])
            for p0 in first_positions:
                match_found = True
                curr_pos = p0
                for next_w in norm_words[1:]:
                    next_positions = self.index.get_postings(next_w).get(doc_id, [])
                    # Allow adjacent (+1) or skip-1 (+2) for punctuation/hyphenation
                    if any(p in next_positions for p in [curr_pos + 1, curr_pos + 2]):
                        curr_pos = next((p for p in [curr_pos + 1, curr_pos + 2] if p in next_positions), curr_pos + 1)
                    else:
                        match_found = False
                        break
                if match_found:
                    matching_docs.add(doc_id)
                    break

        return matching_docs

        return matching_docs

    def execute_boolean_query(self, query_str: str) -> Set[str]:
        """
        Parses and evaluates Boolean query expressions with support for:
        - Quoted phrases: "criminal appeal"
        - AND, OR, NOT operators
        - Relative NOT (e.g. A AND NOT B)
        - Standalone NOT (e.g. NOT A -> all_docs - A)
        """
        all_docs = set(self.index.doc_ids)
        query = query_str.strip()
        if not query:
            return set()

        # Handle 'OR' at top level
        if " OR " in query:
            or_parts = [p.strip() for p in query.split(" OR ")]
            res = set()
            for part in or_parts:
                res = res.union(self.execute_boolean_query(part))
            return res

        # Handle 'AND NOT'
        if " AND NOT " in query:
            left_part, right_part = query.split(" AND NOT ", 1)
            left_set = self.execute_boolean_query(left_part.strip())
            right_set = self.execute_boolean_query(right_part.strip())
            return left_set - right_set

        # Handle standalone 'NOT '
        if query.startswith("NOT "):
            sub_query = query[4:].strip()
            return all_docs - self.execute_boolean_query(sub_query)

        # Handle 'AND'
        if " AND " in query:
            and_parts = [p.strip() for p in query.split(" AND ")]
            res = all_docs.copy()
            for part in and_parts:
                res = res.intersection(self.execute_boolean_query(part))
            return res

        # Handle quoted phrase
        if (query.startswith('"') and query.endswith('"')) or (query.startswith("'") and query.endswith("'")):
            return self.search_phrase(query)

        # Single term or whitespace-separated multiword without explicit operator
        words = query.split()
        if len(words) == 1:
            return self.search_term(words[0])
        else:
            # Multiword implicit phrase or conjunctive search
            phrase_res = self.search_phrase(query)
            if phrase_res:
                return phrase_res
            # Fallback to conjunctive AND
            res = all_docs.copy()
            for w in words:
                res = res.intersection(self.search_term(w))
            return res
