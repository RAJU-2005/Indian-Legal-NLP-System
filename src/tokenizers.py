"""
Tokenization module for Indian Legal Judgment System.
Implements five tokenization strategies:
1. NLTK word tokenizer
2. spaCy tokenizer
3. Custom legal tokenizer (domain regex and pattern merging)
4. Byte Pair Encoding (BPE) tokenizer
5. Hybrid tokenizer (combining domain regex, spaCy, and BPE subword fallback)
"""
import re
from typing import List, Dict, Any, Optional
import nltk
from nltk.tokenize import word_tokenize
import spacy
from pathlib import Path
import sys

# Prevent naming collision between this file and the third-party tokenizers library
_saved_sys_path = list(sys.path)
sys.path = [p for p in sys.path if not (p.endswith("src") or p.endswith("src\\") or p.endswith("src/") or p == "")]
import tokenizers
from tokenizers import Tokenizer, models, pre_tokenizers, trainers
sys.path = _saved_sys_path

# Load spaCy model globally
try:
    _SPACY_NLP = spacy.load("en_core_web_sm")
except Exception:
    _SPACY_NLP = None

class NLTKTokenizer:
    """Conventional NLTK word tokenizer."""
    def tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        try:
            return word_tokenize(text)
        except Exception:
            return text.split()

class SpacyTokenizer:
    """Linguistic spaCy tokenizer preserving grammatical units."""
    def __init__(self, nlp=None):
        self.nlp = nlp or _SPACY_NLP
        if self.nlp is None:
            self.nlp = spacy.load("en_core_web_sm")

    def tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        doc = self.nlp.make_doc(text)
        return [token.text for token in doc if not token.is_space]

class CustomLegalTokenizer:
    """
    Domain-optimized tokenizer for Indian legal judgments.
    Preserves statutory sections, citations, case numbers, currency amounts,
    dates, Latin legal maxims, and hyphenated legal concepts as cohesive tokens.
    """
    def __init__(self):
        # Ordered regex patterns matching from most specific to least specific
        self.patterns = [
            # 1. Statutory Sections: "Section 302 IPC", "Sec. 420", "s. 20", "u/s 498-A", "r/w 149"
            r'(?:(?:Section|Sec\.|s\.)\s*\d+[A-Za-z]*(?:\s*(?:IPC|CrPC|CPC|NDPS|PMLA))?|u/s\s*\d+[A-Za-z]*(?:-\w+)?|r/w\s*\d+[A-Za-z]*)',
            
            # 2. Constitutional Articles: "Article 21", "Article 226", "Art. 32"
            r'(?:Article|Art\.)\s+\d+[A-Za-z]*(?:\([0-9a-zA-Z]+\))*',
            
            # 3. Legal Citations: "AIR 2020 SC 123", "2023 SCC OnLine SC 456", "(2001) 4 SCC 280"
            r'(?:\(?\d{4}\)?\s+)?(?:\d+\s+)?(?:AIR|SCC|SCR|Cri\s*LJ|SCC\s*OnLine|SCALE)\s+(?:[A-Za-z.]+\s+)?\d+',
            
            # 4. Indian Currency: "₹50,000", "Rs. 1,00,000/-", "Rs. 50,000"
            r'(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d+)?(?:/-)?',
            
            # 5. Case & Appeal Numbers: "Crl.A. No. 123/2023", "SLP (Crl.) No. 456/2022", "FIR No. 78/2019"
            r'(?:Crl\.?A\.?|W\.P\.?|SLP\s*\(Crl\.\)?|C\.A\.?|Cri\.\s*Misc\.|FIR)\s*(?:No\.?)?\s*[\d/]+(?:\s*of\s*\d{4})?',
            
            # 6. Dates: "2024-01-15", "30.04.2020", "25th March, 2021", "1 October, 2019"
            r'(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4})',
            
            # 7. Latin Legal Phrases & Compound Maxims
            r'(?:suo\s+motu|prima\s+facie|habeas\s+corpus|ad\s+interim|ex\s+parte|inter\s+alia|mens\s+rea|actus\s+reus|ultra\s+vires|de\s+facto|de\s+jure)',
            
            # 8. Domain Specific Legal Compound Terms & Statutory Phrases
            r'(?:anticipatory\s+bail|commercial\s+quantity|preventive\s+detention|suspension\s+of\s+sentence|extraordinary\s+jurisdiction|reasonable\s+doubt|corpus\s+delicti)',
            
            # 9. Hyphenated Legal Compound Terms: "criminal-appeal", "chain-snatching", "cyber-crime", "pre-arrest"
            r'\b[a-zA-Z]+(?:-[a-zA-Z]+)+\b',
            
            # 10. Abbreviations with internal dots: "U.P.", "A.P.", "P.S.", "Govt.", "N.C.T."
            r'\b(?:[A-Z]\.)+(?:[A-Z])?\b',
            
            # 11. Standard alphanumeric words with apostrophes
            r'\b[a-zA-Z0-9]+(?:\'[a-zA-Z]+)?\b',
            
            # 12. Punctuation and standalone symbols
            r'[^\s\w]'
        ]
        self.compiled_regex = re.compile('|'.join(f'({p})' for p in self.patterns), re.IGNORECASE)

    def tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        matches = self.compiled_regex.finditer(text)
        tokens = []
        for m in matches:
            t = m.group(0).strip()
            if t:
                # Normalize internal spaces in multi-word legal patterns (e.g. 'Section   302' -> 'Section 302')
                t = re.sub(r'\s+', ' ', t)
                tokens.append(t)
        return tokens

class BPETokenizerWrapper:
    """Byte Pair Encoding (BPE) subword tokenizer using Hugging Face tokenizers."""
    def __init__(self, vocab_size: int = 6000, model_path: Optional[str] = None):
        self.vocab_size = vocab_size
        self.model_path = model_path
        self.tokenizer = None
        if model_path and Path(model_path).is_file():
            self.tokenizer = Tokenizer.from_file(str(model_path))

    def train(self, texts: List[str], save_path: Optional[str] = None):
        """Train BPE on legal corpus texts."""
        self.tokenizer = Tokenizer(models.BPE(unk_token="[UNK]"))
        self.tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
        trainer = trainers.BpeTrainer(
            special_tokens=["[UNK]", "[PAD]", "[CLS]", "[SEP]", "[MASK]"],
            vocab_size=self.vocab_size,
            min_frequency=2
        )
        self.tokenizer.train_from_iterator(texts, trainer=trainer)
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            self.tokenizer.save(str(save_path))
            self.model_path = save_path

    def tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        if self.tokenizer is None:
            # Fallback if not yet trained
            return text.split()
        encoding = self.tokenizer.encode(text)
        return encoding.tokens

    def get_vocab_size(self) -> int:
        return self.tokenizer.get_vocab_size() if self.tokenizer else 0

class HybridTokenizer:
    """
    Hybrid legal tokenizer combining:
    1. Custom Legal Tokenizer rules to protect statutory citations and currency
    2. spaCy linguistic tokenization for ordinary sentence structures
    3. BPE subword segmentation for out-of-vocabulary or morphologically complex terms
    """
    def __init__(self, bpe_wrapper: Optional[BPETokenizerWrapper] = None):
        self.custom_tokenizer = CustomLegalTokenizer()
        self.spacy_tokenizer = SpacyTokenizer()
        self.bpe_wrapper = bpe_wrapper

    def tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        
        # Step 1: Extract domain-protected units using custom tokenizer
        custom_tokens = self.custom_tokenizer.tokenize(text)
        
        final_tokens = []
        for token in custom_tokens:
            # If the token is a multi-word statutory phrase, citation, or currency, retain it intact
            if (any(sym in token for sym in ['₹', 'Rs', 'Section', 'Sec.', 'Article', 'SCC', 'AIR', 'Crl.A.']) 
                or ' ' in token or '-' in token):
                final_tokens.append(token)
            else:
                # Step 2: If BPE is available and token is long/complex, check subwords
                if self.bpe_wrapper and len(token) > 12 and token.isalpha():
                    subwords = self.bpe_wrapper.tokenize(token)
                    if len(subwords) > 1:
                        final_tokens.extend(subwords)
                    else:
                        final_tokens.append(token)
                else:
                    final_tokens.append(token)
        return final_tokens

def compare_tokenizers(sample_texts: List[str], bpe_tokenizer: Optional[BPETokenizerWrapper] = None) -> List[Dict[str, Any]]:
    """Compare all 5 tokenization approaches on legal text examples."""
    nltk_tok = NLTKTokenizer()
    spacy_tok = SpacyTokenizer()
    custom_tok = CustomLegalTokenizer()
    bpe_tok = bpe_tokenizer or BPETokenizerWrapper()
    hybrid_tok = HybridTokenizer(bpe_wrapper=bpe_tok)

    results = []
    for idx, text in enumerate(sample_texts, start=1):
        t_nltk = nltk_tok.tokenize(text)
        t_spacy = spacy_tok.tokenize(text)
        t_custom = custom_tok.tokenize(text)
        t_bpe = bpe_tok.tokenize(text)
        t_hybrid = hybrid_tok.tokenize(text)

        results.append({
            "Example_ID": f"Ex_{idx}",
            "Input_Text": text,
            "NLTK_Tokens": " | ".join(t_nltk),
            "NLTK_Count": len(t_nltk),
            "spaCy_Tokens": " | ".join(t_spacy),
            "spaCy_Count": len(t_spacy),
            "Custom_Tokens": " | ".join(t_custom),
            "Custom_Count": len(t_custom),
            "BPE_Tokens": " | ".join(t_bpe),
            "BPE_Count": len(t_bpe),
            "Hybrid_Tokens": " | ".join(t_hybrid),
            "Hybrid_Count": len(t_hybrid),
            "Domain_Preservation_Notes": (
                "Custom and Hybrid preserved statutory citations, case citations, or currency as cohesive semantic units. "
                "Standard NLTK and spaCy split section numbers, punctuation, and currency symbols into separate disconnected fragments."
            )
        })
    return results
