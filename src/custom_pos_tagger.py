"""
Custom POS Taggers for Indian Legal Judgment System:
Approach A: Rule-Based Custom POS Tagger using legal lexicon and syntactic context rules.
Approach B: ML-Based Custom POS Tagger using feature engineering and supervised classification.
"""
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import re
import pandas as pd
import numpy as np
import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

try:
    from config import CUSTOM_POS_RESULTS_CSV, RANDOM_SEED
except ImportError:
    from ..config import CUSTOM_POS_RESULTS_CSV, RANDOM_SEED

class RuleBasedLegalPOSTagger:
    """
    Custom rule-based POS tagger for legal domain.
    Corrects common systematic baseline tagging errors using contextual pattern matching
    and an authoritative legal terminology lexicon.
    """

    # Domain legal term dictionary mapping words to target Penn Treebank tags
    LEGAL_LEXICON: Dict[str, str] = {
        "detenu": "NN",
        "detenus": "NNS",
        "appellant": "NN",
        "appellants": "NNS",
        "respondent": "NN",
        "respondents": "NNS",
        "prosecutrix": "NN",
        "affidavit": "NN",
        "charge-sheet": "NN",
        "habeas": "JJ",
        "corpus": "NN",
        "prima": "JJ",
        "facie": "NN",
        "suo": "RB",
        "motu": "RB",
        "inter": "JJ",
        "alia": "FW",
        "sub-section": "NN",
        "bailable": "JJ",
        "non-bailable": "JJ",
        "anticipatory": "JJ",
        "quashment": "NN",
        "jurisprudence": "NN"
    }

    def __init__(self):
        pass

    def tag(self, tokens: List[str]) -> List[Dict[str, Any]]:
        """
        Tag tokens by running baseline NLTK tagger and applying contextual rules.
        Returns list of dicts with word, default_tag, corrected_tag, rule_applied, changed.
        """
        baseline_tags = pos_tag(tokens)
        results = []
        n = len(tokens)

        for i, (word, base_tag) in enumerate(baseline_tags):
            lower_word = word.lower()
            prev_word = tokens[i - 1].lower() if i > 0 else "<START>"
            next_word = tokens[i + 1].lower() if i < n - 1 else "<END>"
            
            corrected_tag = base_tag
            rule_name = "None"
            changed = False

            # Rule 1: 'learned' preceding legal counsel/advocate/judge is an ADJECTIVE (JJ), not VBN
            if lower_word == "learned" and next_word in {"counsel", "advocate", "judge", "senior", "attorney", "prosecutor"}:
                corrected_tag = "JJ"
                rule_name = "Rule_Learned_Honorific_Adj"
                changed = (corrected_tag != base_tag)

            # Rule 2: 'bail' as NOUN (NN) when preceded by determiners/prepositions/adjectives
            elif lower_word == "bail":
                if prev_word in {"anticipatory", "interim", "regular", "for", "grant", "of", "on", "seek", "seeking", "granted", "the"}:
                    corrected_tag = "NN"
                    rule_name = "Rule_Bail_Contextual_Noun"
                    changed = (corrected_tag != base_tag)
                elif next_word in {"application", "plea", "petition", "order", "bond"}:
                    corrected_tag = "NN"
                    rule_name = "Rule_Bail_Compound_Noun"
                    changed = (corrected_tag != base_tag)

            # Rule 3: 'quashing' as NOUN (NN) when followed by 'of' or preceded by 'for/the'
            elif lower_word in {"quashing", "quash"}:
                if next_word == "of" or prev_word in {"the", "for", "seeking", "praying"}:
                    corrected_tag = "NN"
                    rule_name = "Rule_Quashing_Nominal_Action"
                    changed = (corrected_tag != base_tag)

            # Rule 4: 'bench' as NOUN (NN) when preceded by 'division', 'single', 'full', 'supreme'
            elif lower_word == "bench" and prev_word in {"division", "single", "full", "larger", "constitutional"}:
                corrected_tag = "NN"
                rule_name = "Rule_Bench_Judicial_Noun"
                changed = (corrected_tag != base_tag)

            # Rule 5: 'suo' followed by 'motu' -> Adverbial modifier (RB)
            elif lower_word == "suo" and next_word == "motu":
                corrected_tag = "RB"
                rule_name = "Rule_Suo_Motu_Latin_Adverb"
                changed = (corrected_tag != base_tag)
            elif lower_word == "motu" and prev_word == "suo":
                corrected_tag = "RB"
                rule_name = "Rule_Suo_Motu_Latin_Adverb"
                changed = (corrected_tag != base_tag)

            # Rule 6: Legal Lexicon Direct Match
            elif lower_word in self.LEGAL_LEXICON:
                target_tag = self.LEGAL_LEXICON[lower_word]
                if base_tag != target_tag:
                    corrected_tag = target_tag
                    rule_name = f"Rule_Lexicon_{lower_word.upper()}"
                    changed = True

            results.append({
                "word": word,
                "default_pos": base_tag,
                "custom_pos": corrected_tag,
                "rule_applied": rule_name,
                "changed": changed
            })

        return results


class MLCustomPOSTagger:
    """
    Supervised Machine Learning POS tagger trained on annotated legal sentences.
    Extracts rich morphological and contextual features and trains a logistic regression classifier.
    """

    # Domain legal annotated corpus for training and validation
    TRAINING_CORPUS = [
        [("The", "DT"), ("appellant", "NN"), ("filed", "VBD"), ("an", "DT"), ("appeal", "NN"), ("under", "IN"), ("Section", "NNP"), ("302", "CD"), ("IPC", "NNP"), (".", ".")],
        [("The", "DT"), ("High", "NNP"), ("Court", "NNP"), ("granted", "VBD"), ("anticipatory", "JJ"), ("bail", "NN"), ("to", "TO"), ("the", "DT"), ("accused", "NN"), (".", ".")],
        [("Learned", "JJ"), ("counsel", "NN"), ("for", "IN"), ("the", "DT"), ("petitioner", "NN"), ("sought", "VBD"), ("quashing", "NN"), ("of", "IN"), ("the", "DT"), ("FIR", "NNP"), (".", ".")],
        [("The", "DT"), ("learned", "JJ"), ("advocate", "NN"), ("argued", "VBD"), ("that", "IN"), ("the", "DT"), ("detenu", "NN"), ("was", "VBD"), ("illegally", "RB"), ("detained", "VBN"), (".", ".")],
        [("A", "DT"), ("Division", "NNP"), ("Bench", "NNP"), ("heard", "VBD"), ("the", "DT"), ("habeas", "JJ"), ("corpus", "NN"), ("writ", "NN"), ("petition", "NN"), (".", ".")],
        [("The", "DT"), ("court", "NN"), ("exercised", "VBD"), ("suo", "RB"), ("motu", "RB"), ("jurisdiction", "NN"), ("under", "IN"), ("Article", "NNP"), ("226", "CD"), (".", ".")],
        [("No", "DT"), ("prima", "JJ"), ("facie", "NN"), ("case", "NN"), ("was", "VBD"), ("made", "VBN"), ("out", "RP"), ("against", "IN"), ("the", "DT"), ("respondent", "NN"), (".", ".")],
        [("Commercial", "JJ"), ("quantity", "NN"), ("of", "IN"), ("charas", "NN"), ("was", "VBD"), ("recovered", "VBN"), ("from", "IN"), ("the", "DT"), ("vehicle", "NN"), (".", ".")],
        [("The", "DT"), ("offence", "NN"), ("under", "IN"), ("PMLA", "NNP"), ("is", "VBZ"), ("non-bailable", "JJ"), ("and", "CC"), ("cognizable", "JJ"), (".", ".")],
        [("The", "DT"), ("accused", "NN"), ("was", "VBD"), ("directed", "VBN"), ("to", "TO"), ("execute", "VB"), ("a", "DT"), ("personal", "JJ"), ("bond", "NN"), ("of", "IN"), ("₹50,000", "NNP"), (".", ".")],
        [("The", "DT"), ("learned", "JJ"), ("counsel", "NN"), ("submitted", "VBD"), ("a", "DT"), ("written", "VBN"), ("affidavit", "NN"), (".", ".")],
        [("The", "DT"), ("prosecutrix", "NN"), ("stated", "VBD"), ("that", "IN"), ("she", "PRP"), ("was", "VBD"), ("threatened", "VBN"), ("by", "IN"), ("the", "DT"), ("appellant", "NN"), (".", ".")],
        [("The", "DT"), ("magistrate", "NN"), ("rejected", "VBD"), ("the", "DT"), ("bail", "NN"), ("application", "NN"), ("summarily", "RB"), (".", ".")],
        [("The", "DT"), ("detenu", "NN"), ("has", "VBZ"), ("a", "DT"), ("constitutional", "JJ"), ("right", "NN"), ("under", "IN"), ("Article", "NNP"), ("21", "CD"), (".", ".")],
        [("The", "DT"), ("learned", "JJ"), ("judge", "NN"), ("dismissed", "VBD"), ("the", "DT"), ("revision", "NN"), ("petition", "NN"), (".", ".")]
    ]

    def __init__(self):
        self.vectorizer = DictVectorizer(sparse=True)
        self.model = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
        self.is_trained = False
        self.evaluation_metrics: Dict[str, float] = {}

    def extract_features(self, sentence_tokens: List[str], index: int) -> Dict[str, Any]:
        """Extract morphological, capitalization, and contextual n-gram features for token."""
        word = sentence_tokens[index]
        features = {
            "bias": 1.0,
            "word.lower()": word.lower(),
            "word.isupper()": word.isupper(),
            "word.istitle()": word.istitle(),
            "word.isdigit()": word.isdigit(),
            "word.has_hyphen": "-" in word,
            "word.length": len(word),
            "word[:2]": word[:2].lower(),
            "word[:3]": word[:3].lower(),
            "word[-2:]": word[-2:].lower(),
            "word[-3:]": word[-3:].lower(),
            "is_legal_lexicon": word.lower() in RuleBasedLegalPOSTagger.LEGAL_LEXICON
        }
        if index > 0:
            prev_w = sentence_tokens[index - 1]
            features.update({
                "-1:word.lower()": prev_w.lower(),
                "-1:word.istitle()": prev_w.istitle(),
                "-1:word.isupper()": prev_w.isupper()
            })
        else:
            features["BOS"] = True

        if index < len(sentence_tokens) - 1:
            next_w = sentence_tokens[index + 1]
            features.update({
                "+1:word.lower()": next_w.lower(),
                "+1:word.istitle()": next_w.istitle(),
                "+1:word.isupper()": next_w.isupper()
            })
        else:
            features["EOS"] = True

        return features

    def train_and_evaluate(self, test_split: float = 0.2) -> Dict[str, float]:
        """Train classifier using sentence-level train/test split and calculate metrics."""
        np.random.seed(RANDOM_SEED)
        sentences = list(self.TRAINING_CORPUS)
        np.random.shuffle(sentences)

        split_idx = int(len(sentences) * (1 - test_split))
        train_sents = sentences[:split_idx]
        test_sents = sentences[split_idx:]

        X_train, y_train = [], []
        for s in train_sents:
            tokens = [w for w, tag in s]
            for idx, (w, tag) in enumerate(s):
                X_train.append(self.extract_features(tokens, idx))
                y_train.append(tag)

        X_test, y_test = [], []
        for s in test_sents:
            tokens = [w for w, tag in s]
            for idx, (w, tag) in enumerate(s):
                X_test.append(self.extract_features(tokens, idx))
                y_test.append(tag)

        X_train_vec = self.vectorizer.fit_transform(X_train)
        self.model.fit(X_train_vec, y_train)
        self.is_trained = True

        X_test_vec = self.vectorizer.transform(X_test)
        y_pred = self.model.predict(X_test_vec)

        acc = accuracy_score(y_test, y_pred)
        p, r, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)

        self.evaluation_metrics = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(p), 4),
            "recall": round(float(r), 4),
            "f1_score": round(float(f1), 4),
            "train_sentences": len(train_sents),
            "test_sentences": len(test_sents),
            "train_tokens": len(y_train),
            "test_tokens": len(y_test)
        }
        return self.evaluation_metrics

    def tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """Tag input tokens using the trained ML model."""
        if not self.is_trained:
            self.train_and_evaluate()
        if not tokens:
            return []
        feats = [self.extract_features(tokens, i) for i in range(len(tokens))]
        X = self.vectorizer.transform(feats)
        preds = self.model.predict(X)
        return list(zip(tokens, preds))


def generate_custom_pos_comparison_df() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Produce comprehensive comparison of:
    - Target Legal Word
    - Sentence Context
    - Default POS Tag (NLTK)
    - Custom Rule-Based POS Tag
    - Custom ML-Based POS Tag
    - Ground Truth Expected POS
    - Correction Explanation
    """
    rule_tagger = RuleBasedLegalPOSTagger()
    ml_tagger = MLCustomPOSTagger()
    ml_metrics = ml_tagger.train_and_evaluate()

    test_cases = [
        ("The appellant applied for anticipatory bail under Section 438.", "bail", "NN", "Bail is a substantive legal right/noun, not a verb"),
        ("Learned counsel for the detenu argued that the order was void.", "learned", "JJ", "Honorific judicial adjective modifying counsel, not past verb"),
        ("The petitioner sought quashing of the malicious FIR.", "quashing", "NN", "Gerund nominal functioning as head of noun phrase"),
        ("The High Court took suo motu cognizance of the custodial violence.", "suo", "RB", "Latin adverbial modifier indicating 'on its own motion'"),
        ("The authorities detained the detenu without providing statutory grounds.", "detenu", "NN", "Specialized Indian legal noun for detained person"),
        ("The Division Bench dismissed the commercial appeal.", "bench", "NN", "Judicial forum/collegiate bench noun, not furniture or verb"),
        ("The offence under PMLA is non-bailable and serious.", "non-bailable", "JJ", "Compound statutory adjective qualifying criminal offense")
    ]

    rows = []
    for sentence, target_word, expected_tag, explanation in test_cases:
        tokens = word_tokenize(sentence)
        rule_results = rule_tagger.tag(tokens)
        ml_results = ml_tagger.tag(tokens)

        # Find target word index
        target_idx = None
        for i, t in enumerate(tokens):
            if t.lower() == target_word.lower():
                target_idx = i
                break

        if target_idx is not None:
            r_info = rule_results[target_idx]
            ml_tag = ml_results[target_idx][1]
            default_tag = r_info["default_pos"]
            rule_tag = r_info["custom_pos"]
            rule_name = r_info["rule_applied"]

            rule_correct = "Correct" if rule_tag == expected_tag else "Incorrect"
            default_correct = "Correct" if default_tag == expected_tag else "Incorrect"
            ml_correct = "Correct" if ml_tag == expected_tag else "Incorrect"

            rows.append({
                "Word": target_word,
                "Context Sentence": sentence,
                "Default POS (NLTK)": default_tag,
                "Default Correctness": default_correct,
                "Custom Rule POS": rule_tag,
                "Rule Correctness": rule_correct,
                "Rule Applied": rule_name,
                "Custom ML POS": ml_tag,
                "ML Correctness": ml_correct,
                "Expected POS": expected_tag,
                "Correction Explanation": explanation
            })

    df = pd.DataFrame(rows)
    return df, ml_metrics

def export_custom_pos_csv(output_path: Optional[Path] = None) -> Path:
    """Export custom POS results table to CSV."""
    df, _ = generate_custom_pos_comparison_df()
    out = output_path or CUSTOM_POS_RESULTS_CSV
    df.to_csv(out, index=False, encoding='utf-8')
    return out
