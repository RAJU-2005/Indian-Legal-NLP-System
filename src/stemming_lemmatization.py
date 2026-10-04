"""
Stemming and Lemmatization module for Indian Legal Judgment System.
Implements:
- Porter Stemmer
- Snowball Stemmer
- Lancaster Stemmer
- NLTK WordNet Lemmatizer
- spaCy POS-aware Lemmatizer
Provides detailed legal term comparison and error analysis (over-stemming vs under-stemming).
"""
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import pandas as pd
import spacy
import nltk
from nltk.stem import PorterStemmer, SnowballStemmer, LancasterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

try:
    from config import STEMMING_LEMMATIZATION_CSV
except ImportError:
    from ..config import STEMMING_LEMMATIZATION_CSV

class StemmingLemmatizationAnalyzer:
    """Compares stemming algorithms and POS-aware lemmatization on legal vocabulary."""

    LEGAL_VOCABULARY = [
        ("appellants", "NOUN", "Parties appealing lower court verdict"),
        ("convicted", "VERB", "Found guilty of statutory offense"),
        ("proceedings", "NOUN", "Judicial actions and case hearings"),
        ("execution", "NOUN", "Carrying out of a decree, sentence, or contract"),
        ("executive", "ADJ", "Administrative authority distinct from judiciary"),
        ("prosecutrix", "NOUN", "Female victim/complainant in criminal assault case"),
        ("anticipatory", "ADJ", "Pre-arrest protective relief (bail)"),
        ("judgments", "NOUN", "Formal judicial determinations of court"),
        ("jurisdiction", "NOUN", "Legal authority of court to hear dispute"),
        ("statutory", "ADJ", "Prescribed or enacted by legislation"),
        ("evidentiary", "ADJ", "Relating to evidence admissibility"),
        ("evidence", "NOUN", "Substantive materials presented to prove facts"),
        ("detention", "NOUN", "Confinement or custody of individual"),
        ("conspiracy", "NOUN", "Agreement between parties to commit unlawful act"),
        ("witnesses", "NOUN", "Individuals testifying under oath"),
        ("petitioners", "NOUN", "Parties instituting writ or appeal"),
        ("accused", "NOUN", "Person charged with criminal offense"),
        ("quashing", "VERB", "Nullifying or voiding an FIR or charge-sheet"),
        ("affidavit", "NOUN", "Sworn written declaration of fact"),
        ("sovereignty", "NOUN", "Supreme institutional state authority")
    ]

    def __init__(self):
        self.porter = PorterStemmer()
        self.snowball = SnowballStemmer("english")
        self.lancaster = LancasterStemmer()
        self.wordnet = WordNetLemmatizer()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None

    def get_wordnet_pos(self, treebank_pos: str):
        """Map POS tag to WordNet POS format."""
        if treebank_pos.startswith('J') or treebank_pos == 'ADJ':
            return wordnet.ADJ
        elif treebank_pos.startswith('V') or treebank_pos == 'VERB':
            return wordnet.VERB
        elif treebank_pos.startswith('N') or treebank_pos == 'NOUN':
            return wordnet.NOUN
        elif treebank_pos.startswith('R') or treebank_pos == 'ADV':
            return wordnet.ADV
        else:
            return wordnet.NOUN

    def compare_words(self, words_with_pos: Optional[List[Tuple[str, str, str]]] = None) -> pd.DataFrame:
        """
        Compare Porter, Snowball, Lancaster, WordNet, and spaCy on legal terms.
        """
        targets = words_with_pos or self.LEGAL_VOCABULARY
        rows = []

        for item in targets:
            word, pos_label, context_notes = item[0], item[1], item[2]
            p_stem = self.porter.stem(word)
            s_stem = self.snowball.stem(word)
            l_stem = self.lancaster.stem(word)
            wn_pos = self.get_wordnet_pos(pos_label)
            wn_lemma = self.wordnet.lemmatize(word, pos=wn_pos)

            spacy_lemma = word
            spacy_pos = pos_label
            if self.nlp:
                doc = self.nlp(word)
                if len(doc) > 0:
                    spacy_lemma = doc[0].lemma_
                    spacy_pos = doc[0].pos_

            # Detect over-stemming or under-stemming
            phenomenon = "Normal"
            if word in ["execution", "executive"] and (p_stem == "execut" or s_stem == "execut"):
                phenomenon = "Over-stemming (confounds executive branch with execution of sentence/decree)"
            elif word == "prosecutrix" and p_stem == "prosecutrix":
                phenomenon = "Under-stemming (fails to link with prosecute/prosecutor)"
            elif word == "statutory" and p_stem == "statut":
                phenomenon = "Over-stemming (distorts statutory to non-word 'statut')"
            elif word == "evidentiary" and p_stem == "evidentiari":
                phenomenon = "Over-stemming (leaves unnatural suffix 'evidentiari')"
            elif word == "appellants" and wn_lemma == "appellant":
                phenomenon = "Accurate Lemmatization (retains exact legal singular noun)"

            rows.append({
                "Word": word,
                "Contextual POS": pos_label,
                "Porter Stem": p_stem,
                "Snowball Stem": s_stem,
                "Lancaster Stem": l_stem,
                "WordNet Lemma": wn_lemma,
                "spaCy Lemma": spacy_lemma,
                "Phenomenon / Notes": phenomenon,
                "Legal Distinction": context_notes
            })

        df = pd.DataFrame(rows)
        return df

    def export_comparison_csv(self, output_path: Optional[Path] = None) -> Path:
        """Generate and export stemming vs lemmatization results to CSV."""
        df = self.compare_words()
        out = output_path or STEMMING_LEMMATIZATION_CSV
        df.to_csv(out, index=False, encoding='utf-8')
        return out
