"""
Default POS Tagging module for Indian Legal Judgment System using NLTK and spaCy.
"""
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import pandas as pd
import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize
import spacy

try:
    from config import POS_TAGGING_RESULTS_CSV
except ImportError:
    from ..config import POS_TAGGING_RESULTS_CSV

class DefaultPOSTagger:
    """Runs standard NLTK and spaCy POS tagging over legal sentences."""

    LEGAL_SAMPLE_SENTENCES = [
        ("The appellant applied for anticipatory bail under Section 438 of the Code.", "bail"),
        ("Learned counsel for the detenu argued that preventive detention was unconstitutional.", "detenu"),
        ("The High Court exercised suo motu jurisdiction to review the illegal order.", "suo motu"),
        ("The petitioner sought quashing of the charge-sheet filed under Section 302 IPC.", "quashing"),
        ("Learned counsel submitted that the commercial quantity of charas was not recovered.", "learned"),
        ("The Division Bench granted interim relief to the accused.", "bench"),
        ("The victim filed an affidavit before the trial court.", "affidavit")
    ]

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None

    def tag_nltk(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """Tag tokens using NLTK averaged perceptron tagger."""
        return pos_tag(tokens)

    def tag_spacy(self, text: str) -> List[Tuple[str, str, str]]:
        """Tag text using spaCy, returning (token, coarse_pos, fine_tag)."""
        if self.nlp is None:
            return [(t, "UNK", "UNK") for t in text.split()]
        doc = self.nlp(text)
        return [(t.text, t.pos_, t.tag_) for t in doc]

    def generate_comparison_df(self) -> pd.DataFrame:
        """
        Produce comparison of NLTK and spaCy tagging on legal sample sentences,
        highlighting domain terms and typical baseline mistakes.
        """
        rows = []
        for sentence, focal_term in self.LEGAL_SAMPLE_SENTENCES:
            nltk_tokens = word_tokenize(sentence)
            nltk_tags = dict(self.tag_nltk(nltk_tokens))

            spacy_tags = {}
            if self.nlp:
                doc = self.nlp(sentence)
                for t in doc:
                    spacy_tags[t.text] = (t.pos_, t.tag_)

            # Focus on words in focal_term
            focal_words = focal_term.split()
            for w in focal_words:
                n_tag = nltk_tags.get(w, "N/A")
                sp_pos, sp_tag = spacy_tags.get(w, ("N/A", "N/A"))

                rows.append({
                    "Sentence": sentence,
                    "Target Word": w,
                    "Focal Legal Term": focal_term,
                    "NLTK Tag": n_tag,
                    "spaCy Coarse POS": sp_pos,
                    "spaCy Fine Tag": sp_tag,
                    "Default Behavior Notes": (
                        f"Evaluated behavior of default taggers on legal word '{w}' in context."
                    )
                })

        df = pd.DataFrame(rows)
        return df

    def export_results_csv(self, output_path: Optional[Path] = None) -> Path:
        """Export POS tagging results to CSV."""
        df = self.generate_comparison_df()
        out = output_path or POS_TAGGING_RESULTS_CSV
        df.to_csv(out, index=False, encoding='utf-8')
        return out
