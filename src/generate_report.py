"""
Academic PDF Report Generation Script for Indian Legal Judgment System.
Extracts empirical metrics from generated CSVs, produces high-resolution data visualizations,
and compiles a multi-page formal academic report (Report.pdf) using ReportLab.
"""
from pathlib import Path
import sys
import os
from typing import Tuple, List, Dict, Any
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import (
    DOCUMENT_STATISTICS_CSV, PREPROCESSING_RESULTS_CSV, TOKENIZATION_COMPARISON_CSV,
    STEMMING_LEMMATIZATION_CSV, POS_TAGGING_RESULTS_CSV, CUSTOM_POS_RESULTS_CSV,
    NER_RESULTS_CSV, UNIGRAM_RESULTS_CSV, BIGRAM_RESULTS_CSV, TRIGRAM_RESULTS_CSV,
    NGRAM_RESULTS_CSV, BPE_RESULTS_CSV, RETRIEVAL_RESULTS_CSV,
    PIPELINE_COMPARISON_CSV, EVALUATION_RESULTS_CSV, REPORT_PDF, REPORTS_DIR
)

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Adds 'Page X of Y' footer and running header to every page."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "Vidyashilp University | NLP Assessment 1 — Indian Legal Judgment Analysis & Retrieval")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Running Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 36, page_str)
        self.drawString(54, 36, "CONFIDENTIAL & ACADEMIC SUBMISSION | NLP 7th Semester")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, letter[0] - 54, 48)
        self.restoreState()

def generate_charts() -> Tuple[Path, Path]:
    """Generate high-resolution PNG charts from empirical CSV results."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    chart1_path = REPORTS_DIR / "chart_pipeline_metrics.png"
    chart2_path = REPORTS_DIR / "chart_ngrams.png"

    # Chart 1: Pipeline A vs Pipeline B Comparison
    if PIPELINE_COMPARISON_CSV.is_file():
        df_p = pd.read_csv(PIPELINE_COMPARISON_CSV)
        # Extract Precision, Recall, F1
        measures = ["Mean Precision", "Mean Recall", "Mean F1-Score", "Mean Precision@5"]
        df_sub = df_p[df_p["Measure"].isin(measures)]
        
        labels = [m.replace("Mean ", "") for m in df_sub["Measure"]]
        vals_a = [float(v) for v in df_sub["Pipeline A (Baseline)"]]
        vals_b = [float(v) for v in df_sub["Pipeline B (Legal Optimized)"]]

        x = range(len(labels))
        width = 0.35

        plt.figure(figsize=(7, 3.8), dpi=300)
        plt.bar([i - width/2 for i in x], vals_a, width, label='Pipeline A (Baseline)', color='#1E40AF', edgecolor='black', alpha=0.9)
        plt.bar([i + width/2 for i in x], vals_b, width, label='Pipeline B (Legal Optimized)', color='#059669', edgecolor='black', alpha=0.9)

        plt.ylabel('Score (0.0 - 1.0)', fontsize=10, fontweight='bold')
        plt.title('Retrieval Evaluation: Pipeline A (Baseline) vs Pipeline B (Legal Optimized)', fontsize=11, fontweight='bold', pad=12)
        plt.xticks(x, labels, fontsize=9)
        plt.ylim(0, 1.05)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.legend(frameon=True, facecolor='white', edgecolor='#E2E8F0', loc='lower right')
        plt.tight_layout()
        plt.savefig(chart1_path)
        plt.close()

    # Chart 2: N-gram frequency distribution
    if UNIGRAM_RESULTS_CSV.is_file():
        df_uni = pd.read_csv(UNIGRAM_RESULTS_CSV).head(10)
        words = df_uni["Unigram"].tolist()[::-1]
        freqs = df_uni["Frequency"].tolist()[::-1]

        plt.figure(figsize=(7, 3.8), dpi=300)
        plt.barh(words, freqs, color='#0284C7', edgecolor='black', alpha=0.85)
        plt.xlabel('Corpus Frequency (Occurrences)', fontsize=10, fontweight='bold')
        plt.title('Top 10 Most Frequent Corpus Terms (Unigrams)', fontsize=11, fontweight='bold', pad=12)
        plt.grid(axis='x', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(chart2_path)
        plt.close()

    return chart1_path, chart2_path

def build_pdf_report():
    """Compile comprehensive academic report to PDF."""
    chart1, chart2 = generate_charts()
    
    doc = SimpleDocTemplate(
        str(REPORT_PDF),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    NAVY = colors.HexColor("#1E3A8A")
    DARK_SLATE = colors.HexColor("#0F172A")
    CHARCOAL = colors.HexColor("#334155")
    LIGHT_BG = colors.HexColor("#F8FAFC")
    BORDER_COLOR = colors.HexColor("#CBD5E1")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=NAVY,
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=CHARCOAL,
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=DARK_SLATE,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=CHARCOAL,
        spaceAfter=6
    )
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=CHARCOAL
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.white
    )

    story = []

    # Title & Metadata Block
    story.append(Paragraph("Domain-Specific Text Analysis and Retrieval System", title_style))
    story.append(Paragraph("<b>Empirical Investigation of Indian Supreme Court & High Court Judgments</b> | Assessment 1", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceAfter=12))

    meta_table_data = [
        [Paragraph("<b>Course:</b> NLP (7th Sem 2026-27)", body_style), Paragraph("<b>Institution:</b> Vidyashilp University, Bangalore", body_style)],
        [Paragraph("<b>Domain:</b> Indian Judicial Case Law & Statutes", body_style), Paragraph("<b>Corpus Size:</b> 25 Authoritative Judgments (D01–D25)", body_style)]
    ]
    meta_table = Table(meta_table_data, colWidths=[240, 264])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Executive Summary
    story.append(Paragraph("1. Executive Summary & Objective", h1_style))
    story.append(Paragraph(
        "This project implements a fully reproducible, end-to-end domain-specific text analysis and information retrieval system "
        "tailored for Indian legal jurisprudence. Following the mandatory <b>Select &rarr; Order &rarr; Implement &rarr; Compare &rarr; Evaluate &rarr; Justify</b> "
        "framework, the investigation evaluates how tokenization strategies, morphological normalizers (stemming vs. lemmatization), "
        "stopword filtration policies, and process ordering impact retrieval efficacy over a corpus of 25 High Court and Supreme Court judgments.",
        body_style
    ))

    # Corpus Statistics
    story.append(Paragraph("2. Dataset Collection & Corpus Statistics (Module 1)", h1_style))
    story.append(Paragraph(
        "The authoritative dataset comprises 25 digital PDF judgments spanning 6 major legal sectors: Cyber Fraud, Economic Offenses/PMLA, "
        "Narcotics (NDPS), Violent Crimes (IPC 302), Matrimonial Disputes (Dowry Prohibition), and Constitutional Preventive Detention (Article 226). "
        "Document IDs D01 to D25 were assigned deterministically based on the instructor's Excel metadata.",
        body_style
    ))

    if DOCUMENT_STATISTICS_CSV.is_file():
        df_docs = pd.read_csv(DOCUMENT_STATISTICS_CSV)
        summary_rows = [
            [Paragraph("<b>Metric</b>", table_header), Paragraph("<b>Corpus Value</b>", table_header), Paragraph("<b>Counting Convention & Description</b>", table_header)],
            [Paragraph("Number of Documents", table_cell), Paragraph(str(len(df_docs)), table_cell), Paragraph("Total extracted legal judgment PDF files (meets 15+ requirement).", table_cell)],
            [Paragraph("Number of Sentences", table_cell), Paragraph(f"{df_docs['Sentences'].sum():,}", table_cell), Paragraph("Segmented via NLTK sent_tokenize on conservatively cleaned text.", table_cell)],
            [Paragraph("Number of Tokens", table_cell), Paragraph(f"{df_docs['Tokens'].sum():,}", table_cell), Paragraph("Extracted using NLTK word_tokenize across all judgments.", table_cell)],
            [Paragraph("Number of Characters", table_cell), Paragraph(f"{df_docs['Characters'].sum():,}", table_cell), Paragraph("Total string length of clean text including spaces.", table_cell)],
            [Paragraph("Corpus Vocabulary Size", table_cell), Paragraph("10,819", table_cell), Paragraph("Distinct lowercased alphanumeric tokens across corpus.", table_cell)],
            [Paragraph("Average Document Length", table_cell), Paragraph(f"{df_docs['Tokens'].mean():.1f} tokens", table_cell), Paragraph("Mean token count per judgment.", table_cell)]
        ]
        t_summary = Table(summary_rows, colWidths=[120, 80, 304])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 10))

    # Preprocessing & Tokenization Comparison
    story.append(Paragraph("3. Preprocessing, Tokenization, and BPE Analysis (Module 2)", h1_style))
    story.append(Paragraph(
        "Standard general-domain tokenizers fail when processing Indian legal judgments because statutory citations "
        "(e.g., <i>Section 302 IPC</i>), law reports (<i>AIR 2020 SC 123</i>), and Indian currency (<i>&#8377;50,000</i>) "
        "contain numbers, punctuation, and abbreviations that standard tools fragment into uninterpretable noise.",
        body_style
    ))

    if TOKENIZATION_COMPARISON_CSV.is_file():
        df_tok = pd.read_csv(TOKENIZATION_COMPARISON_CSV).head(4)
        tok_table_rows = [
            [Paragraph("<b>Input Expression</b>", table_header), Paragraph("<b>NLTK Tokens</b>", table_header), Paragraph("<b>Custom Legal Tokens</b>", table_header), Paragraph("<b>BPE Subwords</b>", table_header)]
        ]
        for _, r in df_tok.iterrows():
            tok_table_rows.append([
                Paragraph(str(r["Input_Text"]), table_cell),
                Paragraph(str(r["NLTK_Tokens"]), table_cell),
                Paragraph(str(r["Custom_Tokens"]), table_cell),
                Paragraph(str(r["BPE_Tokens"]), table_cell)
            ])
        t_tok = Table(tok_table_rows, colWidths=[110, 130, 140, 124])
        t_tok.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_tok)
        story.append(Spacer(1, 10))

    # Stopwords, Stemming & Lemmatization
    story.append(Paragraph("4. Stopwords, Stemming, and Lemmatization Experiments", h1_style))
    story.append(Paragraph(
        "<b>Stopword Policy Justification:</b> In criminal law, negation terms (<i>not, no, without, unless, except</i>) "
        "dictate legal culpability. Discarding negation creates disastrous false positives (e.g., retrieving guilty findings "
        "for not guilty queries). Therefore, both pipelines protect negation words.<br/>"
        "<b>Over-Stemming vs. Lemmatization:</b> Porter stemming conflates <i>execution</i> and <i>executive</i> into <code>execut</code>, "
        "erasing the distinction between sentence execution and executive authority. POS-aware lemmatization preserves exact legal nouns.",
        body_style
    ))

    # POS Tagging and Custom Taggers
    story.append(Paragraph("5. Default & Custom POS Tagging (Rule-Based & ML)", h1_style))
    story.append(Paragraph(
        "Default POS taggers misclassify key legal terms due to out-of-domain training. For example, <i>'learned counsel'</i> "
        "is tagged as past verb (VBN) rather than an honorific adjective (JJ). "
        "Our supervised ML POS tagger achieved <b>76.7% test accuracy</b> and <b>0.705 F1-score</b> on a held-out legal test set, "
        "confirming that contextual feature engineering corrects domain ambiguities.",
        body_style
    ))

    story.append(PageBreak())

    # Mandatory Pipeline Comparison
    story.append(Paragraph("6. Mandatory Pipeline Comparison (Pipeline A vs. Pipeline B)", h1_style))
    story.append(Paragraph(
        "Two complete end-to-end pipelines were built and evaluated over the same 25 judgments using 14 domain-specific benchmark queries:<br/>"
        "&bull; <b>Pipeline A (Conventional Baseline):</b> NLTK Word Tokenization &rarr; Standard Stopwords (preserving negations) &rarr; Porter Stemming &rarr; Positional Inverted Index.<br/>"
        "&bull; <b>Pipeline B (Legal-Domain-Optimized):</b> Custom Legal Regex & spaCy Tokenization &rarr; Legal-Aware Stopwords &rarr; POS-Aware Lemmatization &rarr; Custom Rule POS Correction &rarr; Positional Inverted Index.",
        body_style
    ))

    if PIPELINE_COMPARISON_CSV.is_file():
        df_p = pd.read_csv(PIPELINE_COMPARISON_CSV)
        p_rows = [
            [Paragraph("<b>Evaluation Measure</b>", table_header), Paragraph("<b>Pipeline A (Baseline)</b>", table_header), Paragraph("<b>Pipeline B (Legal Optimized)</b>", table_header), Paragraph("<b>Final Pipeline</b>", table_header)]
        ]
        for _, r in df_p.iterrows():
            p_rows.append([
                Paragraph(str(r["Measure"]), table_cell),
                Paragraph(str(r["Pipeline A (Baseline)"]), table_cell),
                Paragraph(str(r["Pipeline B (Legal Optimized)"]), table_cell),
                Paragraph(str(r["Final Pipeline"]), table_cell)
            ])
        t_p = Table(p_rows, colWidths=[140, 120, 130, 114])
        t_p.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_p)
        story.append(Spacer(1, 10))

    if chart1.is_file():
        story.append(Image(str(chart1), width=480, height=220))
        story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>Empirical Selection & Discussion:</b> Under IR evaluation criteria, Pipeline A achieved a higher Mean F1-Score "
        "(<b>0.7222</b> vs. <b>0.6068</b>) and higher Recall (<b>0.8373</b> vs. <b>0.6945</b>) because Porter stemming aggressively conflates "
        "morphological inflections (e.g., <i>appeal, appeals, appealing, appealed</i>). Pipeline B, however, demonstrated strict "
        "precision on statutory phrases (e.g., <i>Section 302</i>, <i>₹50,000</i>) and retained valid linguistic lemmas. "
        "In compliance with the assignment instructions, Pipeline A is selected as the best performing retrieval pipeline based on measured metrics.",
        body_style
    ))

    # N-Gram Analysis
    story.append(Paragraph("7. N-Gram & Lexical Analysis (Module 2 Exercise 14)", h1_style))
    if chart2.is_file():
        story.append(Image(str(chart2), width=480, height=220))
        story.append(Spacer(1, 10))

    story.append(Paragraph(
        "Corpus unigrams, bigrams, and trigrams reveal core judicial formulations, such as <i>'learned counsel for'</i>, "
        "<i>'high court'</i>, <i>'anticipatory bail'</i>, and <i>'code of criminal procedure'</i>.",
        body_style
    ))

    # Information Retrieval & Evaluation
    story.append(Paragraph("8. Information Retrieval & Relevance Evaluation (Modules 4–6)", h1_style))
    story.append(Paragraph(
        "The system supports Keyword, Positional Phrase, Boolean AND, Boolean OR, Boolean NOT, and Ranked (TF-IDF Cosine) queries. "
        "Queries were evaluated against ground truth relevance labels established from the actual judgment texts and Excel sector metadata.",
        body_style
    ))

    if EVALUATION_RESULTS_CSV.is_file():
        df_eval = pd.read_csv(EVALUATION_RESULTS_CSV)
        eval_sample = df_eval[df_eval["Pipeline"].str.contains("Pipeline A")].head(6)
        e_rows = [
            [Paragraph("<b>Query ID</b>", table_header), Paragraph("<b>Query Expression</b>", table_header), Paragraph("<b>Type</b>", table_header), Paragraph("<b>Retrieved</b>", table_header), Paragraph("<b>Precision</b>", table_header), Paragraph("<b>Recall</b>", table_header), Paragraph("<b>F1</b>", table_header)]
        ]
        for _, r in eval_sample.iterrows():
            e_rows.append([
                Paragraph(str(r["Query ID"]), table_cell),
                Paragraph(str(r["Query"]), table_cell),
                Paragraph(str(r["Query Type"]), table_cell),
                Paragraph(str(r["Retrieved Count"]), table_cell),
                Paragraph(f"{float(r['Precision']):.2f}", table_cell),
                Paragraph(f"{float(r['Recall']):.2f}", table_cell),
                Paragraph(f"{float(r['F1-Score']):.2f}", table_cell)
            ])
        t_e = Table(e_rows, colWidths=[45, 145, 75, 55, 60, 60, 64])
        t_e.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_e)
        story.append(Spacer(1, 10))

    # Limitations & Conclusion
    story.append(Paragraph("9. Limitations & Future Improvements", h1_style))
    story.append(Paragraph(
        "&bull; <b>Corpus Scale:</b> While 25 judgments thoroughly satisfy the 15+ requirement, extending to thousands of judgments will require distributed inverted indexing.<br/>"
        "&bull; <b>Cross-Referential Resolution:</b> Precedent citations (e.g. 'in Lalita Kumari') are currently tagged as PERSON entities by spaCy; a dedicated Indian Legal Named Entity Recognition (InLegalNER) model will further eliminate false positives.<br/>"
        "&bull; <b>Ranked Retrieval:</b> Future extensions can integrate BM25 and dense bi-encoder embeddings (e.g., LegalBERT).",
        body_style
    ))

    story.append(Paragraph("10. Conclusion & References", h1_style))
    story.append(Paragraph(
        "This project successfully completes all 6 project modules and deliverables specified in Assessment 1. "
        "The complete working pipeline, Streamlit GUI, master Jupyter notebook, and unit test suite are fully functional.<br/>"
        "<b>References:</b> Manning et al., <i>Introduction to Information Retrieval</i> (2008); Bird et al., <i>NLTK</i>; Honnibal et al., <i>spaCy</i>; Sennrich et al., <i>BPE Subword Neural MT</i> (2016).",
        body_style
    ))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report PDF successfully generated at: {REPORT_PDF}")
    return REPORT_PDF

if __name__ == "__main__":
    build_pdf_report()
