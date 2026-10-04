"""
Configuration module for Indian Legal Judgment Text Analysis & Retrieval System.
Provides deterministic paths, parameters, model identifiers, and result destinations.
"""
from pathlib import Path
import os

# Base directory for the project
BASE_DIR = Path(__file__).resolve().parent

# External source locations on user's machine (as configured by default)
EXTERNAL_DATASET_DIR = Path(r"C:\Users\Admin\Downloads\Dataset_NLP_A1")
EXTERNAL_METADATA_FILE = Path(r"C:\Users\Admin\Downloads\NLP_A1_CaseFiles_Datset_Info.xlsx")

# Local fallback directory inside the project repository
LOCAL_DATASET_DIR = BASE_DIR / "data" / "documents"
LOCAL_METADATA_FILE = BASE_DIR / "data" / "metadata" / "NLP_A1_CaseFiles_Datset_Info.xlsx"

def get_dataset_dir(custom_path: str = None) -> Path:
    """Return effective dataset directory: custom > local (if populated) > external > local."""
    if custom_path and Path(custom_path).is_dir():
        return Path(custom_path)
    if LOCAL_DATASET_DIR.is_dir() and any(LOCAL_DATASET_DIR.glob("*.*")):
        return LOCAL_DATASET_DIR
    if EXTERNAL_DATASET_DIR.is_dir():
        return EXTERNAL_DATASET_DIR
    return LOCAL_DATASET_DIR

def get_metadata_file(custom_path: str = None) -> Path:
    """Return effective metadata file path: custom > local > external."""
    if custom_path and Path(custom_path).is_file():
        return Path(custom_path)
    if LOCAL_METADATA_FILE.is_file():
        return LOCAL_METADATA_FILE
    if EXTERNAL_METADATA_FILE.is_file():
        return EXTERNAL_METADATA_FILE
    return LOCAL_METADATA_FILE

# Output Directories
RESULTS_DIR = BASE_DIR / "results"
REPORTS_DIR = BASE_DIR / "reports"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Result File Paths
DOCUMENT_STATISTICS_CSV = RESULTS_DIR / "document_statistics.csv"
PREPROCESSING_RESULTS_CSV = RESULTS_DIR / "preprocessing_results.csv"
TOKENIZATION_COMPARISON_CSV = RESULTS_DIR / "tokenization_comparison.csv"
STEMMING_LEMMATIZATION_CSV = RESULTS_DIR / "stemming_lemmatization_results.csv"
POS_TAGGING_RESULTS_CSV = RESULTS_DIR / "pos_tagging_results.csv"
CUSTOM_POS_RESULTS_CSV = RESULTS_DIR / "custom_pos_results.csv"
NER_RESULTS_CSV = RESULTS_DIR / "ner_results.csv"
UNIGRAM_RESULTS_CSV = RESULTS_DIR / "unigram_results.csv"
BIGRAM_RESULTS_CSV = RESULTS_DIR / "bigram_results.csv"
TRIGRAM_RESULTS_CSV = RESULTS_DIR / "trigram_results.csv"
NGRAM_RESULTS_CSV = RESULTS_DIR / "ngram_results.csv"
BPE_RESULTS_CSV = RESULTS_DIR / "bpe_results.csv"
INVERTED_INDEX_JSON = RESULTS_DIR / "inverted_index.json"
RETRIEVAL_RESULTS_CSV = RESULTS_DIR / "retrieval_results.csv"
PIPELINE_COMPARISON_CSV = RESULTS_DIR / "pipeline_comparison.csv"
RELEVANCE_JUDGMENTS_CSV = RESULTS_DIR / "relevance_judgments.csv"
EVALUATION_RESULTS_CSV = RESULTS_DIR / "evaluation_results.csv"

# Report Output Path
REPORT_PDF = REPORTS_DIR / "Report.pdf"

# NLP Model Configuration
SPACY_MODEL = "en_core_web_sm"
RANDOM_SEED = 42

# Evaluated Precision@K and Recall@K cutoff values
EVALUATION_K = 5
