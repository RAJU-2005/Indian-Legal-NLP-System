"""
Byte Pair Encoding (BPE) analyzer for Indian Legal Judgment System.
Trains an empirical BPE subword model on the actual corpus documents,
analyzes subword segmentations of common, rare, and domain-specific words,
and exports results to CSV.
"""
import sys

# Prevent naming collision
_saved_sys_path = list(sys.path)
sys.path = [p for p in sys.path if not (p.endswith("src") or p.endswith("src\\") or p.endswith("src/") or p == "")]
import tokenizers
from tokenizers import Tokenizer, models, pre_tokenizers, trainers
sys.path = _saved_sys_path
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd

try:
    from config import BPE_RESULTS_CSV, RESULTS_DIR
    from src.tokenizers import BPETokenizerWrapper, NLTKTokenizer, SpacyTokenizer, CustomLegalTokenizer, HybridTokenizer
except ImportError:
    from ..config import BPE_RESULTS_CSV, RESULTS_DIR
    from .tokenizers import BPETokenizerWrapper, NLTKTokenizer, SpacyTokenizer, CustomLegalTokenizer, HybridTokenizer

class BPEAnalyzer:
    """Manages BPE training, subword breakdown, and comparative vocabulary analytics."""

    SAMPLE_TERMS = [
        # Common general words
        ("the", "Common general"),
        ("court", "Common legal"),
        ("order", "Common legal"),
        ("appeal", "Common legal"),
        ("accused", "Common legal"),
        
        # Rare or compound morphological legal words
        ("jurisprudential", "Rare lexical"),
        ("quashment", "Rare morphological"),
        ("circumstantiality", "Rare morphological"),
        ("non-bailable", "Hyphenated domain"),
        ("unconstitutionality", "Rare morphological"),
        
        # Domain-specific terms & citations
        ("bail", "Domain core"),
        ("anticipatory", "Domain core"),
        ("habeas", "Latin domain"),
        ("corpus", "Latin domain"),
        ("PMLA", "Statutory acronym"),
        ("NDPS", "Statutory acronym"),
        ("Section 302", "Statutory section"),
        ("₹50,000", "Currency token"),
        ("Crl.A. No. 123/2023", "Court appeal citation")
    ]

    def __init__(self, vocab_size: int = 5000):
        self.vocab_size = vocab_size
        self.bpe_model_path = RESULTS_DIR / "bpe_model.json"
        self.bpe_wrapper = BPETokenizerWrapper(vocab_size=vocab_size, model_path=str(self.bpe_model_path))

    def train_on_corpus(self, corpus_texts: List[str]):
        """Train BPE subword tokenizer on actual corpus texts."""
        self.bpe_wrapper.train(corpus_texts, save_path=str(self.bpe_model_path))

    def analyze(self, corpus_texts: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Produce detailed comparison of subword formation and tokenizer behavior.
        """
        if corpus_texts and not self.bpe_model_path.is_file():
            self.train_on_corpus(corpus_texts)

        nltk_tok = NLTKTokenizer()
        spacy_tok = SpacyTokenizer()
        custom_tok = CustomLegalTokenizer()
        hybrid_tok = HybridTokenizer(bpe_wrapper=self.bpe_wrapper)

        rows = []
        for s_no, (term, category) in enumerate(self.SAMPLE_TERMS, start=1):
            bpe_tokens = self.bpe_wrapper.tokenize(term)
            nltk_tokens = nltk_tok.tokenize(term)
            spacy_tokens = spacy_tok.tokenize(term)
            custom_tokens = custom_tok.tokenize(term)
            hybrid_tokens = hybrid_tok.tokenize(term)

            rows.append({
                "S.No.": s_no,
                "Word / Expression": term,
                "Category": category,
                "BPE Tokens": " | ".join(bpe_tokens),
                "BPE Subword Count": len(bpe_tokens),
                "NLTK Tokens": " | ".join(nltk_tokens),
                "spaCy Tokens": " | ".join(spacy_tokens),
                "Custom Tokens": " | ".join(custom_tokens),
                "Hybrid Tokens": " | ".join(hybrid_tokens),
                "Subword Formation Behavior": (
                    "Single unified token" if len(bpe_tokens) == 1 else
                    f"Segmented into {len(bpe_tokens)} subword units: {bpe_tokens}"
                )
            })

        df = pd.DataFrame(rows)
        return df

    def export_results_csv(self, corpus_texts: Optional[List[str]] = None, output_path: Optional[Path] = None) -> Path:
        """Export BPE analysis table to CSV."""
        df = self.analyze(corpus_texts)
        out = output_path or BPE_RESULTS_CSV
        df.to_csv(out, index=False, encoding='utf-8')
        return out
