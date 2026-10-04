"""
Pipeline B: Legal-Domain-Optimized NLP Pipeline for Indian Legal Judgments.
Flow: Conservative Legal Cleaning -> Custom Legal Tokenizer & spaCy Linguistic Tokenization ->
      Domain-Aware Stopword Filtering -> POS-Aware Lemmatization -> Custom Legal POS Correction ->
      Negation Preservation -> Positional Index Tokens.
"""
from typing import Dict, List, Tuple, Any
import re
import spacy
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

try:
    from src.tokenizers import CustomLegalTokenizer
    from src.stopwords_handler import StopwordsHandler
    from src.custom_pos_tagger import RuleBasedLegalPOSTagger
except ImportError:
    from .tokenizers import CustomLegalTokenizer
    from .stopwords_handler import StopwordsHandler
    from .custom_pos_tagger import RuleBasedLegalPOSTagger

class PipelineB:
    """Domain-optimized NLP pipeline for legal retrieval."""

    def __init__(self):
        self.custom_tokenizer = CustomLegalTokenizer()
        self.stopwords_handler = StopwordsHandler()
        self.rule_pos_tagger = RuleBasedLegalPOSTagger()
        self.wordnet_lemmatizer = WordNetLemmatizer()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None

    def get_wordnet_pos(self, tag: str):
        """Map Treebank tag to WordNet POS."""
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('N'):
            return wordnet.NOUN
        elif tag.startswith('R'):
            return wordnet.ADV
        return wordnet.NOUN

    def preprocess_text(self, text: str) -> List[Tuple[str, int]]:
        """
        Process text with legal domain preservation and POS-aware lemmatization.
        Returns list of (normalized_lemma, token_position).
        """
        if not text:
            return []

        # Step 1: Custom Legal Tokenizer extracts domain entities intact
        raw_tokens = self.custom_tokenizer.tokenize(text)

        # Step 2: Apply Rule-Based POS Tagger to resolve domain ambiguities
        tagged_info = self.rule_pos_tagger.tag(raw_tokens)

        processed_tokens_with_pos = []
        pos = 0

        for item in tagged_info:
            tok = item["word"]
            pos_tag = item["custom_pos"]
            lower_tok = tok.lower()

            # Skip punctuation-only tokens unless they are currency/sections
            if not any(c.isalnum() for c in tok) and not any(sym in tok for sym in ['₹', '§', '$']):
                pos += 1
                continue

            # Step 3: Legal-aware stopword filtering (preserves negation words like 'not', 'no', 'without')
            if lower_tok in self.stopwords_handler.legal_stopwords:
                pos += 1
                continue

            # Step 4: POS-aware lemmatization & Domain-Aware Multi-Representation
            if ' ' in tok or any(prefix in tok for prefix in ['Section', 'Sec.', 'Article', '₹', 'Rs', 'Crl.A.']):
                # Index the unified legal domain term
                processed_tokens_with_pos.append((lower_tok, pos))
                pos += 1
                # ALSO index constituent words at subsequent positions so positional phrase search matches
                parts = re.findall(r'\b[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*\b', lower_tok)
                for part in parts:
                    if part not in self.stopwords_handler.legal_stopwords and len(part) > 1:
                        part_lemma = self.wordnet_lemmatizer.lemmatize(part, pos=wordnet.NOUN)
                        processed_tokens_with_pos.append((part_lemma, pos))
                        pos += 1
            else:
                wn_pos = self.get_wordnet_pos(pos_tag)
                normalized_lemma = self.wordnet_lemmatizer.lemmatize(lower_tok, pos=wn_pos)
                processed_tokens_with_pos.append((normalized_lemma, pos))
                pos += 1

        return processed_tokens_with_pos

    def process_corpus(self, documents: Dict[str, Dict[str, Any]]) -> Dict[str, List[Tuple[str, int]]]:
        """Process all documents through Pipeline B."""
        corpus_processed = {}
        for doc_id, doc_data in documents.items():
            text = doc_data["cleaned_text"]
            corpus_processed[doc_id] = self.preprocess_text(text)
        return corpus_processed

    def normalize_query_term(self, term: str) -> str:
        """Normalize a single query term for Pipeline B inverted index."""
        t = term.lower().strip()
        t = re.sub(r'["\']', '', t)
        if t in self.stopwords_handler.legal_stopwords:
            return t
        # If statutory multi-word or citation
        if ' ' in t or any(prefix in t for prefix in ['section', 'sec.', 'article', '₹', 'rs']):
            return t
        # Lemmatize as noun/verb
        return self.wordnet_lemmatizer.lemmatize(t, pos=wordnet.NOUN)
