# Indian Legal Judgment — Domain-Specific Text Analysis & Retrieval System

**Assessment 1 — NLP (Seventh Semester 2026-27)**  
*Vidyashilp University, Bangalore*  
**Framework:** Select → Order → Implement → Compare → Evaluate → Justify

---

## 1. Project Overview & Domain Rationale

This project provides an end-to-end, reproducible, domain-specific text analysis and information retrieval system built for **Indian Supreme Court and High Court judgments**. 

Legal text represents a highly challenging NLP domain characterized by:
- **Statutory Provisions & Multi-Word Citations:** e.g., *Section 302 IPC*, *Article 226*, *NDPS Act s.20*, *AIR 2020 SC 123*.
- **Semantic Polarity of Negation:** Discarding negation words (*not*, *no*, *without*, *unless*) inverts legal culpability (*not guilty* vs. *guilty*).
- **Morphological & Syntactic Ambiguities:** Honorific adjectives like *learned counsel* (frequently misclassified as past verbs by general taggers) or *execution* of a decree vs. *executive* branch.
- **Indian Monetary Expressions:** Bail bonds and sureties such as *₹50,000/-* or *Rs. 1,00,000/-*.

The system ingests 25 authentic Indian legal judgments (`case0078.PDF` to `case1181.PDF`), binds them to authoritative metadata, runs comparative tokenization, stopword policies, stemming vs. lemmatization, rule-based and ML-based custom POS tagging, NER, n-grams, BPE subwords, builds positional inverted indices, evaluates Boolean/Ranked retrieval over 14 legal queries, and provides an interactive Streamlit GUI.

---

## 2. Dataset Information

- **Corpus Size:** 25 Digital PDF Judgments (D01 – D25)
- **Primary Source Path:** `C:\Users\Admin\Downloads\Dataset_NLP_A1`
- **Metadata Excel:** `C:\Users\Admin\Downloads\NLP_A1_CaseFiles_Datset_Info.xlsx`
- **Local Fallback:** `data/documents/` and `data/metadata/`
- **Legal Sectors Represented:**
  1. *Cyber Crime / IT Act* (D01, D02, D03, D04, D05, D17)
  2. *Economic Offenses / PMLA* (D06, D07, D08)
  3. *Narcotics & Psychotropic Substances / NDPS* (D09, D10)
  4. *Violent Crime / Homicide (IPC 302)* (D11, D12, D13)
  5. *Matrimonial Disputes & Dowry Death* (D14, D15)
  6. *Constitutional Habeas Corpus & Preventive Detention* (D21, D22)
  7. *Commercial / Civil / Juvenile Appeals* (D18, D19, D20, D23, D24, D25)

---

## 3. Directory Structure

```text
Domain_Text_Analysis_Retrieval/
│
├── Domain_Text_Analysis_Retrieval.ipynb   # Master executed Jupyter lab manual
├── app.py                                # Interactive Streamlit GUI application
├── requirements.txt                      # Pinned Python package dependencies
├── README.md                             # Comprehensive project documentation
├── config.py                             # Path resolution, hyperparameters, settings
├── Report.pdf                            # Compiled 5-page publication report
├── .gitignore                            # Git exclusion rules
│
├── data/
│   ├── README.md                         # Dataset repository notes
│   ├── documents/                        # 25 preserved case judgment PDFs
│   └── metadata/
│       └── NLP_A1_CaseFiles_Datset_Info.xlsx  # Authoritative case metadata
│
├── src/
│   ├── __init__.py                       # Package initializer
│   ├── document_loader.py                # PDF extractor, metadata matcher, statistics
│   ├── text_cleaner.py                   # Conservative & baseline cleaning
│   ├── tokenizers.py                     # NLTK, spaCy, Custom, BPE, Hybrid tokenizers
│   ├── stopwords_handler.py              # Standard vs. legal-aware stopwords & order test
│   ├── stemming_lemmatization.py         # Porter, Snowball, Lancaster vs WordNet & spaCy
│   ├── pos_tagger.py                     # Default NLTK and spaCy POS tagger
│   ├── custom_pos_tagger.py              # Rule-based & ML-based custom POS taggers
│   ├── ner_processor.py                  # Pretrained spaCy + legal regex entity matcher
│   ├── ngram_analyzer.py                 # Unigrams to 5-grams corpus analytics
│   ├── bpe_analyzer.py                   # Byte Pair Encoding training & subword analysis
│   ├── pipeline_a.py                     # Baseline conventional pipeline implementation
│   ├── pipeline_b.py                     # Domain-optimized legal pipeline implementation
│   ├── inverted_index.py                 # Positional inverted index & TF-IDF vectorizer
│   ├── query_processor.py                # Safe Boolean & positional phrase parser
│   ├── retrieval.py                      # Retrieval engine with contextual snippets
│   ├── evaluation.py                     # 14 Benchmark queries & ground truth IR metrics
│   ├── export_results.py                 # Master pipeline orchestrator & CSV exporter
│   ├── generate_report.py                # Academic PDF report builder (ReportLab)
│   ├── build_notebook.py                 # Master notebook constructor
│   └── utils.py                          # Timing, snippet extraction, and metrics
│
├── results/
│   ├── document_statistics.csv           # Corpus counts (25 docs, 9,402 sents, 257k toks)
│   ├── preprocessing_results.csv         # Before vs. After preprocessing table
│   ├── tokenization_comparison.csv       # 5 tokenizers evaluated on 7 legal inputs
│   ├── stemming_lemmatization_results.csv# Over/under-stemming error analysis
│   ├── pos_tagging_results.csv           # Default tagger outputs on legal sentences
│   ├── custom_pos_results.csv            # Rule & ML corrections (76.7% test accuracy)
│   ├── ner_results.csv                   # General & domain entity evaluation table
│   ├── unigram_results.csv               # Top 50 corpus unigrams
│   ├── bigram_results.csv                # Top 50 corpus bigrams
│   ├── trigram_results.csv               # Top 50 corpus trigrams
│   ├── ngram_results.csv                 # Consolidated 1 to 5-gram summary
│   ├── bpe_results.csv                   # BPE subword segmentation table
│   ├── inverted_index.json               # Serialized positional index
│   ├── retrieval_results.csv             # Query execution log & retrieved IDs
│   ├── pipeline_comparison.csv           # Pipeline A vs Pipeline B empirical metrics
│   ├── relevance_judgments.csv           # Ground truth relevance labels
│   └── evaluation_results.csv            # Precision, Recall, F1, P@5, R@5 per query
│
├── reports/
│   ├── Report.pdf                        # Primary academic report
│   ├── chart_pipeline_metrics.png        # Pipeline A vs B comparison bar chart
│   └── chart_ngrams.png                  # Corpus top terms distribution
│
└── tests/
    ├── test_document_loader.py           # Unit tests for loading and cleaning
    ├── test_tokenizers.py                # Unit tests for domain tokenization rules
    ├── test_query_processor.py           # Unit tests for Boolean logic & phrase search
    ├── test_inverted_index.py            # Unit tests for index postings & TF-IDF
    └── test_evaluation.py                # Unit tests for IR metrics & edge cases
```

---

## 4. Installation & Environment Setup

Run the following commands in **Windows PowerShell**:

```powershell
# 1. Navigate to the project root directory
cd C:\Users\Admin\NLP_A1\Domain_Text_Analysis_Retrieval

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Download language models and NLTK resources
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger_eng')"
```

---

## 5. Execution Instructions

### A. Run Full NLP Experiment Suite (Regenerates all CSVs and JSON):
```powershell
python src/export_results.py
```

### B. Launch Streamlit Web Application:
```powershell
python -m streamlit run app.py
```
*The interactive GUI opens at `http://localhost:8501` featuring search, document inspection, index explorer, and exports.*

### C. Run Unit Test Suite:
```powershell
pytest tests/ -v
```
*(All 18 tests pass in ~14 seconds).*

### D. Re-compile Academic Report PDF:
```powershell
python src/generate_report.py
```

---

## 6. Empirical Findings & Comparison Summary

| Metric | Pipeline A (Baseline) | Pipeline B (Legal-Optimized) | Empirically Selected Final |
| :--- | :---: | :---: | :---: |
| **Total Processed Tokens** | 129,181 | 130,676 | **129,181** |
| **Indexed Vocabulary Size** | 8,355 | 8,868 | **8,355** |
| **Mean Precision** | **0.6924** | 0.5892 | **0.6924** |
| **Mean Recall** | **0.8373** | 0.6945 | **0.8373** |
| **Mean F1-Score** | **0.7222** | 0.6068 | **0.7222** |
| **Mean Precision@5** | **0.7548** | 0.6262 | **0.7548** |
| **Mean Execution Time** | 0.11 ms | 0.06 ms | **0.11 ms** |
| **Domain Term & N-Gram Fidelity** | Partial (Stems truncated) | **High (Citations preserved)** | **Pipeline A for IR Recall / Pipeline B for Semantic Preservation** |

### Key Scientific Insights:
1. **Retrieval Recall vs. Structural Preservation:** Pipeline A's Porter stemmer aggressively conflates inflectional variants (*appealing*, *appealed*, *appeal*), leading to a higher Mean Recall (**0.8373** vs. **0.6945**) and higher Mean F1-Score (**0.7222** vs. **0.6068**). Pipeline B, however, preserves exact legal multi-word entities (*Section 302 IPC*, *₹50,000*) and valid grammatical lemmas.
2. **Stopword Ordering:** Removing stopwords *prior* to stemming avoids morphological mismatch between stemmed words and unstemmed stopword dictionaries.
3. **Custom POS Classification:** The ML-based POS classifier achieved **76.7% accuracy** and **0.705 F1-score** on unseen test sentences, successfully resolving ambiguous tokens like *learned* (JJ), *suo* (RB), and *detenu* (NN).

---

## 7. Deliverables Checklist

- [x] 25 real domain-specific PDF judgments ingested and deterministically mapped (D01–D25).
- [x] All 14 required result files generated from real data (no dummy/placeholder metrics).
- [x] Dual principal pipelines (A & B) implemented and evaluated on 14 benchmark queries.
- [x] Both Rule-Based and ML-Based custom POS taggers trained and evaluated honestly.
- [x] Positional inverted index supporting Keyword, Phrase, Boolean (AND, OR, NOT), and TF-IDF Ranked search.
- [x] Streamlit web application running locally on Windows with all 12 operational views.
- [x] 18 unit tests verified and passing with `pytest`.
- [x] Executed master Jupyter notebook `Domain_Text_Analysis_Retrieval.ipynb`.
- [x] Formal 5-page publication report `Report.pdf` with charts and tables.
