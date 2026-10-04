"""
Pipeline A: Conventional NLP Baseline Pipeline for Indian Legal Judgments.
Flow: Conservative Cleaning -> Lowercasing -> NLTK Tokenization ->
      Standard Stopword Removal (with protected legal negations) -> Porter Stemming.
"""
from typing import Dict, List, Tuple, Any
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

class PipelineA:
    """Conventional NLP baseline processor."""

    def __init__(self):
        self.stemmer = PorterStemmer()
        try:
            raw_stops = set(stopwords.words("english"))
        except Exception:
            raw_stops = {"the", "a", "an", "is", "in", "it", "of", "on", "for", "to", "with", "at", "by"}
        
        # Preserve core negation words even in baseline to prevent complete semantic destruction
        self.protected_negations = {"not", "no", "nor", "neither", "never", "without", "unless", "except"}
        self.stopwords = raw_stops - self.protected_negations

    def preprocess_text(self, text: str) -> List[Tuple[str, int]]:
        """
        Processes text into (stemmed_token, position) sequence.
        Preserves token positions for positional phrase queries.
        """
        if not text:
            return []

        # 1. Basic lowercasing & cleanup
        clean_text = text.lower()
        
        # 2. NLTK word tokenization
        try:
            raw_tokens = word_tokenize(clean_text)
        except Exception:
            raw_tokens = clean_text.split()

        processed_tokens_with_pos = []
        pos = 0
        for tok in raw_tokens:
            # Check if alphanumeric
            if not any(c.isalnum() for c in tok):
                pos += 1
                continue
            
            # 3. Stopword removal
            if tok in self.stopwords:
                pos += 1
                continue

            # 4. Porter Stemming
            stemmed = self.stemmer.stem(tok)
            processed_tokens_with_pos.append((stemmed, pos))
            pos += 1

        return processed_tokens_with_pos

    def process_corpus(self, documents: Dict[str, Dict[str, Any]]) -> Dict[str, List[Tuple[str, int]]]:
        """Process all documents through Pipeline A."""
        corpus_processed = {}
        for doc_id, doc_data in documents.items():
            text = doc_data["cleaned_text"]
            corpus_processed[doc_id] = self.preprocess_text(text)
        return corpus_processed

    def normalize_query_term(self, term: str) -> str:
        """Normalize a single query term to match Pipeline A index."""
        t = term.lower().strip()
        t = re.sub(r'[^\w\s-]', '', t)
        if t in self.stopwords:
            return t
        return self.stemmer.stem(t)
