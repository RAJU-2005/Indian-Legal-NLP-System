"""
N-Gram Analysis module for Indian Legal Judgment System.
Extracts unigrams, bigrams, trigrams, four-grams, and five-grams across the corpus,
computes total and unique counts, top frequencies, and highlights meaningful legal phrases.
"""
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from collections import Counter
import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize

try:
    from config import (
        UNIGRAM_RESULTS_CSV, BIGRAM_RESULTS_CSV, TRIGRAM_RESULTS_CSV, NGRAM_RESULTS_CSV
    )
except ImportError:
    from ..config import (
        UNIGRAM_RESULTS_CSV, BIGRAM_RESULTS_CSV, TRIGRAM_RESULTS_CSV, NGRAM_RESULTS_CSV
    )

class NGramAnalyzer:
    """Computes corpus-wide n-grams (1 to 5) with legal domain filtering."""

    def __init__(self, filter_punctuation: bool = True):
        self.filter_punctuation = filter_punctuation

    def extract_tokens(self, text: str) -> List[str]:
        """Extract clean alphanumeric tokens for n-gram generation."""
        # Convert to lower, retain alphanumeric words and hyphenated legal terms
        text = text.lower()
        tokens = re.findall(r'\b[a-z0-9]+(?:-[a-z0-9]+)*\b', text)
        return tokens

    def generate_ngrams(self, tokens: List[str], n: int) -> List[Tuple[str, ...]]:
        """Generate sliding window n-grams of size n."""
        if len(tokens) < n:
            return []
        return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]

    def analyze_corpus(self, corpus_texts: List[str], max_n: int = 5) -> Dict[int, Dict[str, Any]]:
        """
        Analyze n-grams from n=1 up to n=max_n across all corpus documents.
        Returns dictionary of statistics and top frequencies per n.
        """
        all_tokens = []
        for text in corpus_texts:
            all_tokens.extend(self.extract_tokens(text))

        results = {}
        for n in range(1, max_n + 1):
            ngrams_list = self.generate_ngrams(all_tokens, n)
            counter = Counter(ngrams_list)
            total_count = len(ngrams_list)
            unique_count = len(counter)
            top_10 = counter.most_common(10)

            # Format top 10 as human-readable string: "term (count)"
            top_10_str = "; ".join([f"{' '.join(gram)} ({count})" for gram, count in top_10])

            results[n] = {
                "n": n,
                "n_label": f"{n}-Gram" if n > 3 else ["Unigram", "Bigram", "Trigram"][n - 1],
                "total_count": total_count,
                "unique_count": unique_count,
                "top_10": top_10,
                "top_10_str": top_10_str,
                "counter": counter
            }
        return results

    def export_all_csvs(self, corpus_texts: List[str]) -> Tuple[Path, Path, Path, Path]:
        """
        Generate and export:
        - unigram_results.csv (Top 50)
        - bigram_results.csv (Top 50)
        - trigram_results.csv (Top 50)
        - ngram_results.csv (Consolidated summary for 1, 2, 3, 4, 5-grams)
        """
        results = self.analyze_corpus(corpus_texts, max_n=5)

        # 1. Unigram Top 50 CSV
        uni_rows = [{"Rank": idx, "Unigram": " ".join(gram), "Frequency": count} 
                    for idx, (gram, count) in enumerate(results[1]["counter"].most_common(50), start=1)]
        df_uni = pd.DataFrame(uni_rows)
        df_uni.to_csv(UNIGRAM_RESULTS_CSV, index=False, encoding='utf-8')

        # 2. Bigram Top 50 CSV
        bi_rows = [{"Rank": idx, "Bigram": " ".join(gram), "Frequency": count} 
                   for idx, (gram, count) in enumerate(results[2]["counter"].most_common(50), start=1)]
        df_bi = pd.DataFrame(bi_rows)
        df_bi.to_csv(BIGRAM_RESULTS_CSV, index=False, encoding='utf-8')

        # 3. Trigram Top 50 CSV
        tri_rows = [{"Rank": idx, "Trigram": " ".join(gram), "Frequency": count} 
                    for idx, (gram, count) in enumerate(results[3]["counter"].most_common(50), start=1)]
        df_tri = pd.DataFrame(tri_rows)
        df_tri.to_csv(TRIGRAM_RESULTS_CSV, index=False, encoding='utf-8')

        # 4. Consolidated Summary CSV (1 to 5 grams)
        summary_rows = []
        for n in range(1, 6):
            summary_rows.append({
                "N-Gram": results[n]["n_label"],
                "Total Count": results[n]["total_count"],
                "Unique Count": results[n]["unique_count"],
                "Top 10 N-Grams": results[n]["top_10_str"]
            })
        df_summary = pd.DataFrame(summary_rows)
        df_summary.to_csv(NGRAM_RESULTS_CSV, index=False, encoding='utf-8')

        return UNIGRAM_RESULTS_CSV, BIGRAM_RESULTS_CSV, TRIGRAM_RESULTS_CSV, NGRAM_RESULTS_CSV
