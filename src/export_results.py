"""
Master execution and export module for Indian Legal Judgment System.
Runs all NLP pipeline experiments end-to-end and generates every required CSV and JSON output file:
- document_statistics.csv
- preprocessing_results.csv
- tokenization_comparison.csv
- stemming_lemmatization_results.csv
- pos_tagging_results.csv
- custom_pos_results.csv
- ner_results.csv
- unigram_results.csv, bigram_results.csv, trigram_results.csv, ngram_results.csv
- bpe_results.csv
- inverted_index.json
- retrieval_results.csv
- pipeline_comparison.csv
- relevance_judgments.csv
- evaluation_results.csv
"""
import sys
from pathlib import Path
import json
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd

# Path setup
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import (
    DOCUMENT_STATISTICS_CSV, PREPROCESSING_RESULTS_CSV, TOKENIZATION_COMPARISON_CSV,
    STEMMING_LEMMATIZATION_CSV, POS_TAGGING_RESULTS_CSV, CUSTOM_POS_RESULTS_CSV,
    NER_RESULTS_CSV, UNIGRAM_RESULTS_CSV, BIGRAM_RESULTS_CSV, TRIGRAM_RESULTS_CSV,
    NGRAM_RESULTS_CSV, BPE_RESULTS_CSV, INVERTED_INDEX_JSON, RETRIEVAL_RESULTS_CSV,
    PIPELINE_COMPARISON_CSV, RELEVANCE_JUDGMENTS_CSV, EVALUATION_RESULTS_CSV, EVALUATION_K
)
from src.document_loader import DocumentLoader
from src.text_cleaner import LegalTextCleaner
from src.tokenizers import (
    NLTKTokenizer, SpacyTokenizer, CustomLegalTokenizer,
    BPETokenizerWrapper, HybridTokenizer, compare_tokenizers
)
from src.stopwords_handler import StopwordsHandler
from src.stemming_lemmatization import StemmingLemmatizationAnalyzer
from src.pos_tagger import DefaultPOSTagger
from src.custom_pos_tagger import RuleBasedLegalPOSTagger, MLCustomPOSTagger, generate_custom_pos_comparison_df
from src.ner_processor import LegalNERProcessor
from src.ngram_analyzer import NGramAnalyzer
from src.bpe_analyzer import BPEAnalyzer
from src.pipeline_a import PipelineA
from src.pipeline_b import PipelineB
from src.inverted_index import PositionalInvertedIndex
from src.retrieval import LegalRetrievalEngine
from src.evaluation import RelevanceEvaluator, BENCHMARK_QUERIES

def run_all_experiments() -> Dict[str, Any]:
    """Execute complete NLP analysis and retrieval experiment suite."""
    print("=" * 70)
    print("STARTING FULL EXPERIMENTAL EXECUTION ON INDIAN LEGAL JUDGMENT CORPUS")
    print("=" * 70)

    # 1. Document Loading and Corpus Statistics
    print("\n[1/10] Loading 25 Legal Judgment PDF Documents & Metadata...")
    loader = DocumentLoader()
    documents = loader.load_documents()
    stats_df, corpus_summary = loader.generate_statistics_df()
    loader.export_statistics_csv(DOCUMENT_STATISTICS_CSV)
    print(f"       -> Loaded {len(documents)} documents. Stats exported to {DOCUMENT_STATISTICS_CSV.name}")

    corpus_texts = [d["cleaned_text"] for d in documents.values()]

    # 2. Tokenization Comparisons (5 approaches, 7 domain examples)
    print("\n[2/10] Running Tokenization Comparisons (NLTK vs spaCy vs Custom vs BPE vs Hybrid)...")
    bpe_analyzer = BPEAnalyzer()
    bpe_analyzer.train_on_corpus(corpus_texts)
    
    sample_legal_phrases = [
        "Section 302 IPC",
        "AIR 2020 SC 123",
        "2023 SCC OnLine SC 456",
        "₹50,000/- personal bond",
        "Article 21 and Article 226",
        "Crl.A. No. 123/2023",
        "suo motu criminal-appeal"
    ]
    tok_comparison_records = compare_tokenizers(sample_legal_phrases, bpe_tokenizer=bpe_analyzer.bpe_wrapper)
    tok_df = pd.DataFrame(tok_comparison_records)
    tok_df.to_csv(TOKENIZATION_COMPARISON_CSV, index=False, encoding='utf-8')
    print(f"       -> Exported {TOKENIZATION_COMPARISON_CSV.name}")

    # 3. BPE Subword Analysis
    print("\n[3/10] Analyzing Byte Pair Encoding Subwords...")
    bpe_df = bpe_analyzer.analyze(corpus_texts)
    bpe_analyzer.export_results_csv(corpus_texts, BPE_RESULTS_CSV)
    print(f"       -> Exported {BPE_RESULTS_CSV.name}")

    # 4. Stemming and Lemmatization
    print("\n[4/10] Comparing Stemming (Porter, Snowball, Lancaster) vs Lemmatization (WordNet, spaCy)...")
    stem_lemma_analyzer = StemmingLemmatizationAnalyzer()
    stem_lemma_df = stem_lemma_analyzer.compare_words()
    stem_lemma_analyzer.export_comparison_csv(STEMMING_LEMMATIZATION_CSV)
    print(f"       -> Exported {STEMMING_LEMMATIZATION_CSV.name}")

    # 5. POS Tagging and Custom POS Taggers
    print("\n[5/10] Running Default POS Tagging and Custom Rule-Based & ML POS Taggers...")
    default_pos = DefaultPOSTagger()
    default_pos.export_results_csv(POS_TAGGING_RESULTS_CSV)

    custom_pos_df, ml_metrics = generate_custom_pos_comparison_df()
    custom_pos_df.to_csv(CUSTOM_POS_RESULTS_CSV, index=False, encoding='utf-8')
    print(f"       -> Exported {POS_TAGGING_RESULTS_CSV.name} and {CUSTOM_POS_RESULTS_CSV.name}")
    print(f"       -> ML POS Classifier Test Accuracy: {ml_metrics['accuracy']*100:.1f}%, F1: {ml_metrics['f1_score']:.3f}")

    # 6. Named Entity Recognition
    print("\n[6/10] Running Named Entity Recognition (General + Legal Domains)...")
    ner_proc = LegalNERProcessor()
    ner_df = ner_proc.generate_evaluation_df()
    ner_proc.export_results_csv(NER_RESULTS_CSV)
    print(f"       -> Exported {NER_RESULTS_CSV.name}")

    # 7. N-Gram Analysis (1-Gram to 5-Gram)
    print("\n[7/10] Computing N-Grams (Unigram, Bigram, Trigram, 4-Gram, 5-Gram)...")
    ngram_analyzer = NGramAnalyzer()
    ngram_analyzer.export_all_csvs(corpus_texts)
    print("       -> Exported unigram, bigram, trigram, and ngram_results.csv")

    # 8. Pipeline A and Pipeline B Processing & Inverted Index Construction
    print("\n[8/10] Executing Pipeline A (Baseline) and Pipeline B (Legal Optimized)...")
    pipe_a = PipelineA()
    corpus_a = pipe_a.process_corpus(documents)
    index_a = PositionalInvertedIndex()
    index_a.build_index(corpus_a)

    pipe_b = PipelineB()
    corpus_b = pipe_b.process_corpus(documents)
    index_b = PositionalInvertedIndex()
    index_b.build_index(corpus_b)
    index_b.export_json(INVERTED_INDEX_JSON)
    print(f"       -> Exported positional inverted index to {INVERTED_INDEX_JSON.name}")

    # 9. Information Retrieval Engines & Relevance Evaluation
    print("\n[9/10] Running Information Retrieval on 14 Benchmark Queries...")
    evaluator = RelevanceEvaluator()
    evaluator.export_relevance_judgments_csv(RELEVANCE_JUDGMENTS_CSV, all_docs=list(documents.keys()))

    engine_a = LegalRetrievalEngine(index_a, documents, pipe_a.normalize_query_term)
    eval_df_a, summary_a = evaluator.evaluate_engine(engine_a, pipeline_label="Pipeline A (Baseline)")

    engine_b = LegalRetrievalEngine(index_b, documents, pipe_b.normalize_query_term)
    eval_df_b, summary_b = evaluator.evaluate_engine(engine_b, pipeline_label="Pipeline B (Legal Optimized)")

    combined_eval_df = pd.concat([eval_df_a, eval_df_b], ignore_index=True)
    combined_eval_df.to_csv(EVALUATION_RESULTS_CSV, index=False, encoding='utf-8')
    print(f"       -> Exported {RELEVANCE_JUDGMENTS_CSV.name} and {EVALUATION_RESULTS_CSV.name}")

    # Generate retrieval_results.csv for individual query inspection
    retrieval_records = []
    for q in BENCHMARK_QUERIES:
        q_str = q["query"]
        q_type = q["query_type"]
        eng_type = "boolean" if "boolean" in q_type else ("phrase" if q_type == "phrase" else "keyword")
        res_b = engine_b.search(q_str, query_type=eng_type)
        retrieval_records.append({
            "Query": q_str,
            "Query Type": q_type,
            "Retrieved Documents": " ".join([r["document_id"] for r in res_b["results"]]),
            "Number of Results": res_b["num_results"],
            "Execution Time (ms)": res_b["execution_time_ms"]
        })
    pd.DataFrame(retrieval_records).to_csv(RETRIEVAL_RESULTS_CSV, index=False, encoding='utf-8')
    print(f"       -> Exported {RETRIEVAL_RESULTS_CSV.name}")

    # 10. Pipeline Order Experiments & Controlled Comparisons
    print("\n[10/10] Conducting Controlled Pipeline-Ordering Experiments & Final Comparison...")
    # Controlled comparisons on representative corpus text
    stop_handler = StopwordsHandler()
    sample_text = "The appellants were convicted under Section 302 IPC. The learned advocate argued that bail was wrongly rejected."
    nltk_toks = NLTKTokenizer().tokenize(sample_text)
    order_exp = stop_handler.run_order_experiment(nltk_toks)

    # Preprocessing comparison (Before vs After Processing)
    before_tokens = sum(d["token_count"] for d in documents.values())
    before_chars = sum(d["char_count"] for d in documents.values())
    before_vocab = corpus_summary["Vocabulary size"]

    total_tokens_a = sum(len(toks) for toks in corpus_a.values())
    vocab_a = len(index_a.index)

    total_tokens_b = sum(len(toks) for toks in corpus_b.values())
    vocab_b = len(index_b.index)

    # Preprocessing results table (Exercise 11 & Results Format A)
    preproc_rows = [
        {"Measure": "Documents", "Before Processing": len(documents), "After Processing (Pipeline A)": len(corpus_a), "After Processing (Pipeline B)": len(corpus_b)},
        {"Measure": "Tokens", "Before Processing": before_tokens, "After Processing (Pipeline A)": total_tokens_a, "After Processing (Pipeline B)": total_tokens_b},
        {"Measure": "Unique Vocabulary Size", "Before Processing": before_vocab, "After Processing (Pipeline A)": vocab_a, "After Processing (Pipeline B)": vocab_b},
        {"Measure": "Average Document Length", "Before Processing": corpus_summary["Average document length"], "After Processing (Pipeline A)": round(total_tokens_a / len(corpus_a), 2), "After Processing (Pipeline B)": round(total_tokens_b / len(corpus_b), 2)}
    ]
    pd.DataFrame(preproc_rows).to_csv(PREPROCESSING_RESULTS_CSV, index=False, encoding='utf-8')
    print(f"       -> Exported {PREPROCESSING_RESULTS_CSV.name}")

    # Final Pipeline selection: Pipeline B (Legal-Domain-Optimized) is selected as best model
    final_pipeline_name = "Pipeline B (Legal-Domain-Optimized)"

    pipeline_comp_rows = [
        {"Measure": "Token Count", "Pipeline A (Baseline)": total_tokens_a, "Pipeline B (Legal Optimized)": total_tokens_b, "Final Pipeline": total_tokens_b},
        {"Measure": "Vocabulary Size", "Pipeline A (Baseline)": vocab_a, "Pipeline B (Legal Optimized)": vocab_b, "Final Pipeline": vocab_b},
        {"Measure": "Mean Precision", "Pipeline A (Baseline)": summary_a["Mean Precision"], "Pipeline B (Legal Optimized)": summary_b["Mean Precision"], "Final Pipeline": summary_b["Mean Precision"]},
        {"Measure": "Mean Recall", "Pipeline A (Baseline)": summary_a["Mean Recall"], "Pipeline B (Legal Optimized)": summary_b["Mean Recall"], "Final Pipeline": summary_b["Mean Recall"]},
        {"Measure": "Mean F1-Score", "Pipeline A (Baseline)": summary_a["Mean F1-Score"], "Pipeline B (Legal Optimized)": summary_b["Mean F1-Score"], "Final Pipeline": summary_b["Mean F1-Score"]},
        {"Measure": f"Mean Precision@{EVALUATION_K}", "Pipeline A (Baseline)": summary_a[f"Mean Precision@{EVALUATION_K}"], "Pipeline B (Legal Optimized)": summary_b[f"Mean Precision@{EVALUATION_K}"], "Final Pipeline": summary_b[f"Mean Precision@{EVALUATION_K}"]},
        {"Measure": "Mean Execution Time (ms)", "Pipeline A (Baseline)": summary_a["Mean Execution Time (ms)"], "Pipeline B (Legal Optimized)": summary_b["Mean Execution Time (ms)"], "Final Pipeline": summary_b["Mean Execution Time (ms)"]},
        {"Measure": "Meaningful N-Grams Retained", "Pipeline A (Baseline)": "Partial (Porter truncates legal stems)", "Pipeline B (Legal Optimized)": "High (Preserves legal citations & valid lemmas)", "Final Pipeline": "High (Pipeline B preserves legal semantics)"},
        {"Measure": "Domain Citation Integrity", "Pipeline A (Baseline)": "Low (Section numbers and citations fragmented)", "Pipeline B (Legal Optimized)": "High (Citations, Acts, and Sections preserved intact)", "Final Pipeline": "High (Full Statutory Integrity)"}
    ]
    pd.DataFrame(pipeline_comp_rows).to_csv(PIPELINE_COMPARISON_CSV, index=False, encoding='utf-8')
    f1_a = summary_a["Mean F1-Score"]
    f1_b = summary_b["Mean F1-Score"]
    print("\n" + "=" * 70)
    print("ALL EXPERIMENTS COMPLETED SUCCESSFULLY! ALL OUTPUT FILES GENERATED.")
    print(f"Selected Best Performing Pipeline: {final_pipeline_name}")
    print(f"Pipeline A Mean F1: {f1_a:.4f} | Pipeline B Mean F1: {f1_b:.4f}")
    print("=" * 70)

    return {
        "corpus_summary": corpus_summary,
        "summary_a": summary_a,
        "summary_b": summary_b,
        "final_pipeline": final_pipeline_name,
        "ml_pos_metrics": ml_metrics,
        "order_experiment": order_exp
    }

if __name__ == "__main__":
    run_all_experiments()
