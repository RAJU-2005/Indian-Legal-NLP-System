"""
Evaluation module for Indian Legal Judgment Retrieval System.
Defines 14 authoritative domain-specific queries, manages ground-truth relevance judgments,
computes Precision, Recall, F1, Precision@K, Recall@K, and execution times across pipelines,
and exports results to CSV.
"""
from typing import List, Dict, Any, Tuple, Optional, Set
from pathlib import Path
import pandas as pd

try:
    from config import RELEVANCE_JUDGMENTS_CSV, EVALUATION_RESULTS_CSV, EVALUATION_K
    from src.utils import calculate_precision_recall_f1, calculate_precision_recall_at_k
except ImportError:
    from ..config import RELEVANCE_JUDGMENTS_CSV, EVALUATION_RESULTS_CSV, EVALUATION_K
    from .utils import calculate_precision_recall_f1, calculate_precision_recall_at_k

# 14 Authoritative Benchmark Legal Queries
BENCHMARK_QUERIES = [
    {
        "query_id": "Q01",
        "query": "cyber",
        "query_type": "keyword",
        "description": "Legal cyber offences and computer fraud cases",
        "relevant_docs": ["D01", "D02", "D03", "D04", "D05"],
        "notes": "Cases involving IT Act 66-D/66-G and cyber crime police station investigations."
    },
    {
        "query_id": "Q02",
        "query": "bail",
        "query_type": "keyword",
        "description": "Judgments considering grant, rejection, or cancellation of bail",
        "relevant_docs": ["D01", "D02", "D03", "D06", "D07", "D09", "D10", "D11", "D12", "D15", "D16", "D17", "D18"],
        "notes": "Judgments with active bail determination under CrPC Sections 437, 438, 439."
    },
    {
        "query_id": "Q03",
        "query": '"anticipatory bail"',
        "query_type": "phrase",
        "description": "Pre-arrest protective relief under Section 438 CrPC",
        "relevant_docs": ["D07", "D11", "D15", "D17"],
        "notes": "Explicit anticipatory bail applications under Section 438 CrPC."
    },
    {
        "query_id": "Q04",
        "query": "PMLA",
        "query_type": "keyword",
        "description": "Prevention of Money Laundering Act enforcement actions",
        "relevant_docs": ["D06", "D07", "D08"],
        "notes": "Directorate of Enforcement money laundering prosecutions under PMLA 2002."
    },
    {
        "query_id": "Q05",
        "query": '"habeas corpus"',
        "query_type": "phrase",
        "description": "Constitutional writ challenging unlawful preventive detention",
        "relevant_docs": ["D21", "D22"],
        "notes": "Writs under Article 226 and Supreme Court challenges to detention orders."
    },
    {
        "query_id": "Q06",
        "query": "NDPS",
        "query_type": "keyword",
        "description": "Narcotic Drugs and Psychotropic Substances Act offences",
        "relevant_docs": ["D09", "D10"],
        "notes": "Prosecutions under NDPS Act Section 20 and 8/21 for contraband possession."
    },
    {
        "query_id": "Q07",
        "query": "bail AND appeal",
        "query_type": "boolean_and",
        "description": "Appellate proceedings adjudicating bail or suspension of sentence",
        "relevant_docs": ["D06", "D07", "D11", "D12", "D16", "D18", "D19", "D20"],
        "notes": "Intersection of appellate jurisdiction and bail applications."
    },
    {
        "query_id": "Q08",
        "query": "forgery AND cheating",
        "query_type": "boolean_and",
        "description": "Financial deception cases under IPC Sections 420, 467, 468",
        "relevant_docs": ["D01", "D03", "D24"],
        "notes": "Joint invocation of cheating and falsification of documents."
    },
    {
        "query_id": "Q09",
        "query": "cyber OR extortion",
        "query_type": "boolean_or",
        "description": "Disjunctive query for technological crime or extortion offences",
        "relevant_docs": ["D01", "D02", "D03", "D04", "D05", "D17"],
        "notes": "Union of cases citing IT Act provisions or coercive financial extortion."
    },
    {
        "query_id": "Q10",
        "query": "bail AND NOT murder",
        "query_type": "boolean_not",
        "description": "Bail determinations in non-homicide criminal proceedings",
        "relevant_docs": ["D01", "D02", "D03", "D06", "D07", "D09", "D10", "D16", "D17"],
        "notes": "Excludes violent homicide trials (IPC 302) from bail consideration."
    },
    {
        "query_id": "Q11",
        "query": '"commercial quantity"',
        "query_type": "phrase",
        "description": "Strict threshold under Section 37 NDPS Act for narcotics bail",
        "relevant_docs": ["D09", "D10"],
        "notes": "Rigorous statutory bar on bail for commercial narcotics haul."
    },
    {
        "query_id": "Q12",
        "query": '"Section 302"',
        "query_type": "phrase",
        "description": "Indian Penal Code capital murder prosecution",
        "relevant_docs": ["D11", "D12", "D13", "D14", "D18", "D23"],
        "notes": "Direct invocation of murder charges under Section 302 IPC."
    },
    {
        "query_id": "Q13",
        "query": "detenu",
        "query_type": "keyword",
        "description": "Preventive detention subject challenging detention grounds",
        "relevant_docs": ["D21", "D22"],
        "notes": "Incarcerated individual in preventive detention under State security laws."
    },
    {
        "query_id": "Q14",
        "query": "dowry",
        "query_type": "keyword",
        "description": "Matrimonial harassment and dowry death under IPC 498A/304B",
        "relevant_docs": ["D14", "D15"],
        "notes": "Prosecutions under Dowry Prohibition Act and IPC matrimonial sections."
    },
    {
        "query_id": "Q15",
        "query": "executive",
        "query_type": "keyword",
        "description": "Judgments involving executive magistrates, detention authorities, or executive action",
        "relevant_docs": ["D09", "D14", "D18", "D20", "D23"],
        "notes": "Tests Porter over-stemming collision (execution vs executive) where Pipeline A suffers false positives."
    }
]

class RelevanceEvaluator:
    """Evaluates IR performance across query set using ground truth relevance judgments."""

    def __init__(self, queries: Optional[List[Dict[str, Any]]] = None):
        self.queries = queries or BENCHMARK_QUERIES

    def export_relevance_judgments_csv(self, output_path: Optional[Path] = None, all_docs: Optional[List[str]] = None) -> Path:
        """
        Export authoritative relevance judgments table:
        query_id, query, query_type, document_id, relevance_label, reviewer_notes.
        """
        doc_list = all_docs or [f"D{i:02d}" for i in range(1, 26)]
        rows = []
        for q in self.queries:
            qid = q["query_id"]
            query_str = q["query"]
            q_type = q["query_type"]
            rel_set = set(q["relevant_docs"])
            notes = q["notes"]

            for doc_id in doc_list:
                label = 1 if doc_id in rel_set else 0
                rows.append({
                    "query_id": qid,
                    "query": query_str,
                    "query_type": q_type,
                    "document_id": doc_id,
                    "relevance_label": label,
                    "reviewer_notes": notes if label == 1 else "Not primarily relevant to query scope."
                })

        df = pd.DataFrame(rows)
        out = output_path or RELEVANCE_JUDGMENTS_CSV
        df.to_csv(out, index=False, encoding='utf-8')
        return out

    def evaluate_engine(self, engine, pipeline_label: str = "Pipeline") -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Run all benchmark queries on the retrieval engine and calculate metrics:
        Precision, Recall, F1, Precision@K, Recall@K, Retrieved Count, Execution Time.
        """
        rows = []
        all_precisions = []
        all_recalls = []
        all_f1s = []
        all_p_at_k = []
        all_r_at_k = []
        all_times = []

        for q in self.queries:
            qid = q["query_id"]
            query_str = q["query"]
            q_type = q["query_type"]
            ground_truth = q["relevant_docs"]

            # Map benchmark query type to engine query type
            engine_type = "boolean" if "boolean" in q_type else ("phrase" if q_type == "phrase" else "keyword")
            res = engine.search(query_str, query_type=engine_type)

            retrieved = [item["document_id"] for item in res["results"]]
            time_ms = res["execution_time_ms"]

            prec, rec, f1 = calculate_precision_recall_f1(retrieved, ground_truth)
            p_k, r_k = calculate_precision_recall_at_k(retrieved, ground_truth, k=EVALUATION_K)

            all_precisions.append(prec)
            all_recalls.append(rec)
            all_f1s.append(f1)
            all_p_at_k.append(p_k)
            all_r_at_k.append(r_k)
            all_times.append(time_ms)

            rows.append({
                "Pipeline": pipeline_label,
                "Query ID": qid,
                "Query": query_str,
                "Query Type": q_type,
                "Retrieved Documents": " ".join(retrieved) if retrieved else "None",
                "Retrieved Count": len(retrieved),
                "Ground Truth Count": len(ground_truth),
                "Precision": prec,
                "Recall": rec,
                "F1-Score": f1,
                f"Precision@{EVALUATION_K}": p_k,
                f"Recall@{EVALUATION_K}": r_k,
                "Execution Time (ms)": time_ms
            })

        df = pd.DataFrame(rows)

        summary_metrics = {
            "Pipeline": pipeline_label,
            "Mean Precision": round(float(pd.Series(all_precisions).mean()), 4),
            "Mean Recall": round(float(pd.Series(all_recalls).mean()), 4),
            "Mean F1-Score": round(float(pd.Series(all_f1s).mean()), 4),
            f"Mean Precision@{EVALUATION_K}": round(float(pd.Series(all_p_at_k).mean()), 4),
            f"Mean Recall@{EVALUATION_K}": round(float(pd.Series(all_r_at_k).mean()), 4),
            "Mean Execution Time (ms)": round(float(pd.Series(all_times).mean()), 2)
        }

        return df, summary_metrics

    def export_evaluation_results_csv(self, df_results: pd.DataFrame, output_path: Optional[Path] = None) -> Path:
        """Export evaluation metrics to CSV."""
        out = output_path or EVALUATION_RESULTS_CSV
        df_results.to_csv(out, index=False, encoding='utf-8')
        return out
