"""
Stopword handling module for Indian Legal Judgment System.
Provides standard NLTK stopword filtering and a domain-tailored legal stopword handler
that protects negations, statutory exceptions, and jurisdictional qualifiers.
"""
from typing import List, Set, Dict, Any, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

class StopwordsHandler:
    """Manages baseline and legal-aware stopword filtering."""

    # Essential legal negation and condition tokens that must NEVER be discarded
    PROTECTED_LEGAL_TERMS: Set[str] = {
        "not", "no", "nor", "neither", "never", "without", "unless",
        "except", "against", "cannot", "non", "anti", "under", "between",
        "before", "upon", "within", "inter", "prima", "facie", "ultra", "vires"
    }

    def __init__(self):
        try:
            self.nltk_stopwords: Set[str] = set(stopwords.words("english"))
        except Exception:
            self.nltk_stopwords = {
                "the", "a", "an", "in", "on", "at", "by", "for", "with", "about",
                "against", "between", "into", "through", "during", "before", "after",
                "above", "below", "to", "from", "up", "down", "in", "out", "on", "off",
                "over", "under", "again", "further", "then", "once", "here", "there",
                "when", "where", "why", "how", "all", "any", "both", "each", "few",
                "more", "most", "other", "some", "such", "no", "nor", "not", "only",
                "own", "same", "so", "than", "too", "very", "s", "t", "can", "will",
                "just", "don", "should", "now"
            }

        # Legal-aware stopwords: NLTK stopwords MINUS protected legal terms
        self.legal_stopwords: Set[str] = self.nltk_stopwords - self.PROTECTED_LEGAL_TERMS

    def filter_standard(self, tokens: List[str]) -> List[str]:
        """Filter using standard NLTK stopwords (lowercased)."""
        return [t for t in tokens if t.lower() not in self.nltk_stopwords]

    def filter_legal_aware(self, tokens: List[str]) -> List[str]:
        """Filter using legal-aware stopwords, preserving essential negation and condition words."""
        return [t for t in tokens if t.lower() not in self.legal_stopwords]

    def run_order_experiment(self, tokens: List[str]) -> Dict[str, Any]:
        """
        Controlled experiment for Exercise 9:
        Order 1: Stopword removal -> Stemming
        Order 2: Stemming -> Stopword removal
        """
        stemmer = PorterStemmer()

        # Order 1: Stopword removal -> Stemming
        tokens_filtered_first = self.filter_legal_aware(tokens)
        tokens_stemmed_after = [stemmer.stem(t) for t in tokens_filtered_first]

        # Order 2: Stemming -> Stopword removal
        tokens_stemmed_first = [stemmer.stem(t) for t in tokens]
        tokens_filtered_after = self.filter_legal_aware(tokens_stemmed_first)

        return {
            "Original_Count": len(tokens),
            "Original_Vocab": len(set(tokens)),
            "Order1_Stopwords_Then_Stemming_Count": len(tokens_stemmed_after),
            "Order1_Stopwords_Then_Stemming_Vocab": len(set(tokens_stemmed_after)),
            "Order2_Stemming_Then_Stopwords_Count": len(tokens_filtered_after),
            "Order2_Stemming_Then_Stopwords_Vocab": len(set(tokens_filtered_after)),
            "Analysis": (
                "When stemming precedes stopword removal (Order 2), morphological stems may no longer "
                "match the unstemmed stopword dictionary (e.g. 'having' stems to 'have', 'being' to 'be', "
                "or words are altered such that stopword lookup misses them). Therefore, filtering stopwords "
                "before stemming (Order 1) ensures consistent stopword recognition and avoids unintended vocabulary bloat."
            )
        }
