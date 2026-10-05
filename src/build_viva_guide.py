import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
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
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "NLP Assessment 1 · Individual Observations & Viva Defense Guide")
            self.drawRightString(558, 750, "Vidyashilp University · 2026")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)
        
        # Footer
        text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, text)
        self.drawString(54, 36, "Confidential · Team: Brunda, Shreerenu, Lavanya, Raju")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()

def build_pdf_and_md():
    md_content = """# NLP Assessment 1: Individual Task Observations & Viva Defense Guide
## Domain-Specific Text Analysis and Retrieval System for Indian Legal Judgments

**Course:** Natural Language Processing (Assessment 1, Seventh Semester)  
**Institution:** School of Advanced Computing, Vidyashilp University  
**Team Members:**  
1. **Brunda** (Data Ingestion, Conservative Cleaning & Baseline Tokenization/Stemming)  
2. **Shreerenu** (Stopwords, Baseline Pipeline A Architecture & Word Inverted Index)  
3. **Lavanya** (Custom Legal Regex Tokenizer, ML POS Tagger & Legal NER)  
4. **Raju** (Contextual Lemmatization, Dual-Level Index, IR Engine & Live Evaluation)  

---

# PART 1: INDIVIDUAL TASK OBSERVATIONS & ENGINEERING FINDINGS

### 👤 Member 1: Brunda (Data Ingestion, Text Cleaning & Baseline Stemming)
1. **Corpus Ingestion & OCR Line-Break Hyphenation:** Ingested 25 full-text digital PDF judgments (257,849 tokens, 8,552 sentences) from the Supreme Court and 6 High Courts. A primary observation was that scanned and court-formatted PDFs frequently contain broken words across line breaks (e.g., `crimi-\\nnal`, `prose-\\ncution`). Without proactive de-hyphenation, vocabulary counts artificially inflate, and search queries for "criminal" fail to match words broken across line wraps.
2. **Destructive Impact of Aggressive Text Cleaning:** Aggressive cleaning purges all non-alphanumeric characters indiscriminately. In judicial texts, this erases Indian Rupee markers (`₹50,000/-` becomes `50 000`, fragmented into two numbers) and deletes statutory sub-clause brackets (`Section 376(2)(i) IPC` becomes `section 376 2 i ipc`). Stripping sub-clause brackets destroys the aggravated statutory child rape threshold under the POCSO Act harmonization. Conservative cleaning was engineered to preserve 100% of these statutory boundaries.
3. **Empirical Benchmarking of Porter vs. Snowball vs. Lancaster:**
   - *Lancaster Stemmer Failure:* Lancaster uses hyper-aggressive iterative replacement rules that destroy legal semantics: `legal` -> `leg` (conflating the legal profession with an anatomical human leg!), `custody` -> `cust` (truncated into meaningless noise), `bailment` -> `bail` (conflating civil contracts under Indian Contract Act Section 148 with criminal surety bail!), and `appellants` -> `appl` (conflating court litigants with an apple or an application).
   - *Why Porter over Snowball?* On our 257k legal tokens, Porter and Snowball produce **98.4% identical roots**. Crucially, Snowball fails on the exact same legal collisions as Porter (`execution` & `executive` both become `execut`; `suit` & `suitable` both become `suit`). Porter (1980) was selected for baseline Pipeline A because it is the canonical reference standard in IR literature (Manning et al., 2008). Using Porter establishes an academically recognized baseline proving that suffix stripping itself is fundamentally inadequate for Indian law.
4. **Penn Treebank Citation Splitting:** Standard NLTK Word Tokenization splits compound citations at spaces, periods, and parentheses (`Section 302 IPC` -> `['Section', '302', 'IPC']`; `AIR 2020 SC 1450` -> `['AIR', '2020', 'SC', '1450']`). This forces downstream indexing to treat citations as separate words, requiring expensive positional joins.

---

### 👤 Member 2: Shreerenu (Stopword Polarity Policy, Pipeline A Architecture & Positional Index)
1. **The Catastrophic Liability Inversion Problem:** Standard NLTK stopword lists remove 179 functional words including `not`, `no`, `without`, `unless`, and `against`. In criminal jurisprudence, dropping these words reverses legal reality: `"applicant is not guilty"` becomes `['applicant', 'guilty']`, and `"no grounds for detention"` becomes `['grounds', 'detention']`. A query for judgments where an accused was "not guilty" retrieves only cases where the accused was found "guilty", causing precision to collapse to 0%.
2. **The 8-Term Protected Stopword Policy:** Created a strict polarity whitelist protecting 8 terms (`not`, `no`, `never`, `without`, `unless`, `except`, `until`, `against`). While filtering out non-semantic grammar fluff (`the`, `is`, `at`, `hereto`), this policy compressed the corpus from 257,849 tokens to 129,181 tokens (a **49.9% corpus compression**), while retaining 100% of criminal polarity conditions. Both Pipeline A and Pipeline B incorporate this policy.
3. **Word-Level Positional Inverted Index Structure:** Implemented an in-memory positional inverted index indexing 8,355 unique stemmed terms across all 25 documents. Each entry maps a term to a postings dictionary of document IDs and coordinate tuples `(sentence_idx, word_offset)`. Average query latency is 0.14 ms.
4. **Mathematical Demonstration of Stemmer Bottlenecks:**
   - *Collision 1 (`execution` vs `executive`):* Porter truncates decree `execution` and `executive` magistrate to `execut`. Searching for `"executive"` in Pipeline A retrieves 13 judgments: 5 true executive cases (D09, D14, D18, D20, D23) and 8 false positives from civil decree executions (D24, D25, D01), resulting in a dismal **38.5% precision**!
   - *Collision 2 (`suit` vs `suitable`):* Porter strips both to `suit`. Searching for `"suit"` retrieves 17 judgments: 10 civil partition/money suits and 7 false positives from employment cases where an accommodation or candidate was deemed "suitable", reducing precision to **58.8%**.
   - *Positional Merge Overhead:* Searching for multi-word phrases like `"anticipatory bail"` requires iterative $O(N+M)$ coordinate adjacency verification across separate postings lists.

---

### 👤 Member 3: Lavanya (Custom Legal Regex Tokenizer, ML POS Tagger & Legal NER)
1. **Custom Legal Regex Cascades:** Engineered prioritized regular expressions for Pipeline B that treat statutory provisions, monetary sums, and Latin maxims as atomic single tokens:
   - Input: `"Bail under Section 438 CrPC of ₹50,000/-"`
   - Pipeline A (NLTK): 10 fragmented tokens (`['Bail', 'under', 'Section', '438', 'CrPC', 'of', '₹', '50,000', '/', '-']`).
   - Pipeline B (Custom Regex): 5 clean atomic tokens (`['Bail', 'under', 'Section 438 CrPC', 'of', '₹50,000/-']`).
   This eliminates downstream coordinate joins for compound legal citations.
2. **Penn Treebank Syntax Failures on Case Law:** Documented systematic failures of default NLTK POS taggers on legal text:
   - `"learned counsel"`: `learned` tagged as `VBD` (Past Verb) instead of `JJ` (Honorific Adjective).
   - `"quashing of FIR"`: `quashing` tagged as `VBG` (Participle Verb) instead of `NN` (Legal Remedy Noun).
   - `"suo motu"`: `suo` tagged as `NN` instead of `RB` (Adverbial Motion Modifier).
   - `"the bench"`: `bench` tagged as `NN` (Furniture) instead of `NNP` (Judicial Panel).
   - `"ad-interim bail"`: `ad-interim` split into unknown tokens instead of `JJ` (Interlocutory Modifier).
3. **Supervised ML Logistic Regression POS Classifier:** Trained a multi-class Logistic Regression classifier with L2 regularization using contextual n-gram features (character suffixes 2-4, prefixes, title case, neighboring word windows). On a 20% held-out test split of annotated Indian court sentences, it achieved **76.7% Test Accuracy** and **0.705 Weighted F1-Score**, successfully predicting `learned` as `JJ` ($P=0.882$) and `quashing` as `NN` ($P=0.914$).
4. **Domain-Specific Legal NER:** Implemented rule-based extraction for 4 domain-specific legal categories (`LEGAL_SECTION`, `LEGAL_STATUTE`, `LEGAL_COURT`, `LEGAL_CITATION`) and standard entities (`PERSON`, `ORG`, `MONEY`, `GPE`). Built an interactive visualizer into Streamlit for real-time entity filtering.
5. **Statistical N-Grams & BPE Subwords:** Discovered that legal text is dominated by multi-word collocations (`high court`: 1,842; `learned counsel`: 1,650; `anticipatory bail`: 432; `code of criminal procedure`: 245). Trained a 6,000-vocabulary Byte Pair Encoding (BPE) subword tokenizer that handles rare words like `unconstitutional` (`un` + `constitution` + `al`) and `non-bailable` (`non` + `-` + `bail` + `able`) without out-of-vocabulary fallback.

---

### 👤 Member 4: Raju (Contextual Lemmatization, Dual-Level Index, IR Engine, Evaluation & GUI Demo)
1. **Contextual POS Lemmatization Resolves Collisions:** Replaced algorithmic suffix stripping with WordNet and spaCy lemmatizers guided by part-of-speech context:
   - `execution` [Noun] -> `execution`; `executive` [Noun/Adj] -> `executive` (Precision increases from 38.5% to **100.0% 🏆**, 0 false positives).
   - `suit` [Noun] -> `suit`; `suitable` [Adjective] -> `suitable` (Precision increases from 58.8% to **100.0% 🏆**, 0 false positives).
   - `learned` [Adjective] -> `learned`; `learning` [Verb] -> `learn` (Judicial honorific preserved).
2. **Dual-Level Atomic Positional Index Architecture:** Engineered a two-layer index structure indexing 9,005 terms (+650 compound legal entities over Pipeline A):
   - *Layer 1 (Atomic Compound Keys):* Stores intact phrases like `'section 302 ipc'` -> `{'D11': [14, 82], 'D12': [5], 'D18': [23, 91]}`. Querying a statutory section is a direct $O(1)$ dictionary lookup, eliminating coordinate merges.
   - *Layer 2 (Constituent Lemmas):* Retains single lemmatized tokens for flexible keyword queries.
   - *Latency Speedup:* Reduces query execution time from 0.14 ms to **0.04 ms (3.5× faster!)**.
3. **Advanced Multi-Mode IR Engine:**
   - *Boolean Shunting-Yard Parser:* Implemented Dijkstra's Shunting-Yard algorithm supporting operator precedence (`NOT` > `AND` > `OR`) and exact phrase evaluation (e.g., `"anticipatory bail" AND NOT murder`).
   - *Vector Space TF-IDF Cosine Retrieval:* Implemented sublinear term frequency scoring $\text{TF-IDF}(t,d) = (1 + \log \text{TF}_{t,d}) \times \log(N/\text{DF}_t)$ normalized against Euclidean document length.
4. **Controlled Evaluation Across 15 Benchmark Queries:**
   - Mean Precision: 0.7089 (Pipeline A) vs. **0.7721 (Pipeline B)** -> **+8.9% Precision Boost 🏆**
   - Mean Recall: 0.8904 (Pipeline A) vs. **0.8904 (Pipeline B)** -> **100% Recall Retained (Tie)**
   - Mean F1-Score: 0.7549 (Pipeline A) vs. **0.7979 (Pipeline B)** -> **+5.7% Harmonic Gain 🏆**
   - Precision@5: 0.7444 (Pipeline A) vs. **0.8111 (Pipeline B)** -> **+9.0% Density Improvement 🏆**
   - Query Latency: 0.14 ms (Pipeline A) vs. **0.04 ms (Pipeline B)** -> **3.5× Faster Execution 🏆**
   *Verdict:* Pipeline B conclusively wins. It eliminates false positives without sacrificing recall.
5. **Interactive Streamlit GUI & Live Telemetry:** Built a 17-page dark navy dashboard featuring real-time IR metric cards and an academic Forensic IR Execution Trace calculating TP, FP, and FN live on any user query.

---

# PART 2: 25 COMPREHENSIVE VIVA QUESTIONS & MODEL ANSWERS

### 🎤 Category 1: Questions for Brunda (Ingestion, Cleaning, Tokenization & Stemming)

**Q1: Why did you choose Conservative Cleaning over Aggressive Cleaning for legal judgments?**  
*Model Answer:* "In general NLP, aggressive cleaning purges all non-alphanumeric symbols. In Indian case law, this is disastrous. For example, `₹50,000/-` becomes `50 000`, stripping the rupee symbol and splitting the amount into two numbers. Furthermore, `Section 376(2)(i) IPC` becomes `section 376 2 i ipc`, deleting the parentheses that define the specific aggravated child rape clause under the POCSO Act harmonization. Our conservative cleaning normalizes whitespace and repairs line-break hyphenations while strictly preserving statutory brackets, currency symbols, and quotes."

**Q2: What specific defect occurs when standard NLTK Word Tokenizer is used on legal citations?**  
*Model Answer:* "The standard NLTK tokenizer uses Penn Treebank regular expressions, which treat periods, slashes, and spaces within citations as general word boundaries. It fragments `Section 302 IPC` into three disconnected tokens: `['Section', '302', 'IPC']`. In downstream retrieval, a search for Section 302 will match any document containing the word 'Section' or the number '302' unless expensive positional coordinate merges are performed."

**Q3: Why did you reject the Lancaster Stemmer in favor of the Porter Stemmer?**  
*Model Answer:* "Lancaster uses hyper-aggressive, iterative suffix-stripping rules that mutilate legal morphology. In our experiments, Lancaster stripped `legal` to `leg` (conflating law with the human body), `custody` to `cust`, `bailment` to `bail` (conflating civil contracts under Indian Contract Act Section 148 with criminal surety bail), and `appellant` to `appl`. Porter uses calibrated 5-step rules that preserve the basic word root, avoiding such grotesque truncations."

**Q4: If Snowball and Porter produce virtually identical results, why did you pick Porter for Pipeline A?**  
*Model Answer:* "On our 257k legal tokens, Porter and Snowball produce 98.4% identical roots. Crucially, Snowball fails on the exact same legal polysemes as Porter—both collapse `execution` and `executive` to `execut`, and both collapse `suit` and `suitable` to `suit`. Porter (1980) was chosen because it is the canonical, universally recognized baseline in IR benchmark literature (Manning et al., 2008). Using Porter establishes an academically recognized baseline proving that algorithmic suffix stripping itself is fundamentally inadequate for legal retrieval."

**Q5: How did you handle OCR hyphenation errors across line wraps in court PDFs?**  
*Model Answer:* "Digital court PDFs often break words across line boundaries with hyphens, such as `crimi-\\nnal` or `prose-\\ncution`. In our conservative normalization pass, we used regular expression lookarounds to detect alphabetic tokens split by a hyphen and a newline character, recombining them into their intact single word (`criminal`, `prosecution`). This prevented artificial vocabulary inflation and preserved token continuity."

---

### 🎤 Category 2: Questions for Shreerenu (Stopwords, Inverted Index & Pipeline A)

**Q6: Why can't we use standard English stopword lists in criminal jurisprudence?**  
*Model Answer:* "Standard stopword lists remove negation words like `not`, `no`, `without`, `unless`, and `against`. In criminal law, stripping these words causes Catastrophic Liability Inversion. For instance, `\"the applicant is not guilty\"` is stripped to `['applicant', 'guilty']`, and `\"no offence is made out\"` becomes `['offence', 'made']`. A search for judgments of acquittal retrieves judgments of conviction! Precision collapses to 0% on negative condition queries."

**Q7: What is your Protected Stopword Policy and what corpus compression did it achieve?**  
*Model Answer:* "Our policy whitelists 8 critical polarity and conditional operators: `not`, `no`, `never`, `without`, `unless`, `except`, `until`, and `against`. Non-semantic filler words like `the`, `is`, `at`, and `wherein` are filtered out. Across our corpus, this reduced raw tokens from 257,849 to 129,181, achieving a **49.9% corpus compression** while preserving 100% of criminal polarity conditions."

**Q8: Explain the data structure of your Word-Level Positional Inverted Index in Pipeline A.**  
*Model Answer:* "In Pipeline A, the index is a hash map where each key is a stemmed vocabulary term (8,355 unique stems). The value is a postings dictionary mapping each document ID to a list of coordinate tuples: `(sentence_index, word_offset)`. For example, `execut` maps to `{'D08': [(14, 3), (42, 11)], 'D24': [(112, 7)]}`. This allows verifying whether two stemmed words appear in adjacent positions."

**Q9: Explain the over-stemming collision in Pipeline A with the 'executive' query.**  
*Model Answer:* "The word `execution` refers to decree enforcement under the Code of Civil Procedure, while `executive` refers to executive magistrates under the CrPC. The Porter stemmer truncates both words to `execut`. When a user searches for `\"executive\"`, Pipeline A loads the postings for `execut` and retrieves 13 judgments. Only 5 are true executive magistrate cases; 8 are civil decree executions. Precision collapses to **38.5%**."

**Q10: Explain the second over-stemming collision in Pipeline A: 'suit' vs. 'suitable'.**  
*Model Answer:* "The legal noun `suit` refers to civil title or partition lawsuits under the CPC, while `suitable` is an ordinary English adjective used in employment or service jurisprudence (e.g., 'suitable accommodation', 'suitable candidate'). Porter strips both words to `suit`. A search for `\"suit\"` retrieves 17 judgments, 7 of which are employment or service disputes having nothing to do with civil suits, plunging precision to **58.8%**."

---

### 🎤 Category 3: Questions for Lavanya (Custom Regex, ML POS Tagging & Legal NER)

**Q11: How does your Custom Legal Regex Tokenizer prevent citation fragmentation?**  
*Model Answer:* "Our tokenizer uses prioritized regular expression cascades that match entire statutory citations (`Section 302 IPC`), constitutional articles (`Article 21`), monetary conditions (`₹50,000/-`), and Latin maxims (`suo motu`) before falling back to general word matching. For example, `Bail under Section 438 CrPC of ₹50,000/-` is tokenized into 5 atomic tokens instead of 10 fragmented tokens."

**Q12: Why does the Penn Treebank POS tagger fail on phrases like 'learned counsel'?**  
*Model Answer:* "The Penn Treebank tagger was trained on the Wall Street Journal, where `learned` almost always functions as the past tense or participle form of the verb 'to learn' (`VBN` or `VBD`). In judicial text, `learned` is an honorific adjective (`JJ`) modifying counsel or judge. Our custom POS rules and ML classifier correctly classify it as `JJ` based on its syntactic position before legal nouns."

**Q13: What features did you engineer for your Supervised ML POS Classifier?**  
*Model Answer:* "We engineered contextual n-gram features: character suffixes of length 2 to 4 (`-ing`, `-tion`, `-able`, `-ed`), prefixes (`un-`, `non-`), orthographic flags (`is_title`, `is_upper`, `has_digit`, `has_hyphen`), and preceding and following word tokens. We trained a Multi-Class Logistic Regression model with L2 regularization on Indian court text, achieving **76.7% Test Accuracy** and **0.705 Weighted F1-Score**."

**Q14: What domain-specific entities does your Legal NER module extract?**  
*Model Answer:* "Our Legal NER module extracts four statutory domain entities: `LEGAL_SECTION` (e.g., `Section 438 CrPC`), `LEGAL_STATUTE` (e.g., `NDPS Act`, `PMLA`), `LEGAL_COURT` (e.g., `Supreme Court of India`), and `LEGAL_CITATION` (e.g., `AIR 2020 SC 123`). It also extracts standard entities: `PERSON` (judges, accused), `ORG` (ED, CBI), `MONEY` (bail surety amounts), and `GPE` (states and jurisdictions)."

**Q15: Why did you train a Byte Pair Encoding (BPE) model with a 6,000 vocabulary?**  
*Model Answer:* "Legal text contains complex morphological compounds, Latin prefixes, and hyphenated terms. Traditional word tokenizers replace unseen words with `<UNK>`. Our 6,000-vocabulary BPE model iteratively merges frequent character pairs, allowing rare words like `unconstitutional` to be segmented into `un` + `constitution` + `al`, and `non-bailable` into `non` + `-` + `bail` + `able`, eliminating out-of-vocabulary loss."

---

### 🎤 Category 4: Questions for Raju (Lemmatization, Dual-Level Index, IR Engine & Evaluation)

**Q16: How does contextual lemmatization in Pipeline B resolve the 'executive' collision?**  
*Model Answer:* "Unlike stemmers that chop word endings using static suffix rules, WordNet and spaCy lemmatizers check morphological dictionaries conditioned on part-of-speech tags. Because our ML POS tagger tags `execution` as a Noun and `executive` as an Adjective/Noun, lemmatization preserves `execution` and `executive` as distinct dictionary lemmas. Querying `\"executive\"` retrieves only the 5 true cases, achieving **100% precision** with zero false positives."

**Q17: Explain the Dual-Level Atomic Positional Index and why it is 3.5× faster.**  
*Model Answer:* "In Pipeline A, searching for `Section 302 IPC` requires loading three separate postings lists (`section`, `302`, `ipc`) and running an iterative coordinate merge checking if `pos(302) == pos(section) + 1`. In Pipeline B, the index has two layers: Layer 1 indexes intact compound phrases (`'section 302 ipc'`) directly. A search for this citation is a single $O(1)$ hash table lookup. Layer 2 indexes constituent lemmas for single-word queries. This direct lookup reduced query latency from 0.14 ms to **0.04 ms (3.5× faster)**."

**Q18: How does your Boolean Retrieval Engine parse queries like '\"anticipatory bail\" AND NOT murder'?**  
*Model Answer:* "We implemented Dijkstra's Shunting-Yard algorithm to convert infix Boolean queries into Reverse Polish Notation (postfix). Operator precedence is enforced: `NOT` has highest precedence, followed by `AND`, followed by `OR`. Quoted phrases are treated as atomic tokens. The engine evaluates the postfix stack using set operations: it computes the intersection of postings for `anticipatory bail` and takes the set difference with postings for `murder`."

**Q19: Explain the mathematical formula for your Vector Space TF-IDF Cosine Retrieval.**  
*Model Answer:* "We compute sublinear term frequency: $\text{TF}(t,d) = 1 + \log(\text{TF}_{t,d})$ for $\text{TF} > 0$. The inverse document frequency is $\text{IDF}(t) = \log(N / \text{DF}_t)$, where $N=25$. The query-document score is the cosine angle:
$$\text{Score}(q, d) = \frac{\sum_{t \in q} \text{TF-IDF}(t,d) \cdot \text{TF-IDF}(t,q)}{\sqrt{\sum_{t \in d} \text{TF-IDF}(t,d)^2} \cdot \sqrt{\sum_{t \in q} \text{TF-IDF}(t,q)^2}}$$
Normalizing by Euclidean document length eliminates bias toward lengthy High Court judgments."

**Q20: Walk us through the 15-query benchmark evaluation. Why is Pipeline B the winning model?**  
*Model Answer:* "Across 15 legal benchmark queries, Pipeline B achieved:
  - Mean Precision: **0.7721 vs. 0.7089 (+8.9% gain)**
  - Mean Recall: **0.8904 vs. 0.8904 (100% recall retained)**
  - Mean F1-Score: **0.7979 vs. 0.7549 (+5.7% harmonic gain)**
  - Precision@5: **0.8111 vs. 0.7444 (+9.0% top-ranked density)**
  - Latency: **0.04 ms vs. 0.14 ms (3.5× faster)**
Pipeline B is the winning model because it decisively improves precision and retrieval speed without sacrificing a single point of recall."

---

### 🎤 Category 5: Cross-Cutting Viva Questions (All Members)

**Q21: In IR evaluation, there is usually a Precision-Recall trade-off. Why did Pipeline B improve Precision WITHOUT dropping Recall?**  
*Model Answer:* "In traditional IR, precision is boosted by narrowing search criteria, which often drops recall by excluding borderline cases. In our legal domain, however, Pipeline A's low precision was caused by artificial false positives from stemmer collisions (`execut` matching decree cases) and fragmented citations. Pipeline B did not narrow the search space arbitrarily—it eliminated linguistic false positives through POS-aware lemmatization and atomic citation preservation while retaining all true relevant documents, thereby preserving 100% of the recall (0.8904)."

**Q22: How would your system scale if the corpus grew from 25 judgments to 100,000 judgments?**  
*Model Answer:* "Currently, our postings lists reside in in-memory Python dictionaries with JSON persistence. At 100,000 documents:
  1. We would migrate from in-memory hash maps to disk-based inverted indexes using Block Sort-Based Indexing (BSBI) or Single-Pass In-Memory Indexing (SPIMI).
  2. We would compress postings lists using Variable Byte (Varint) or Elias-Gamma gap encoding.
  3. Layer 1 atomic compound indexing would be limited to statutory entities extracted by NER to prevent vocabulary explosion."

**Q23: What is the significance of the Forensic IR Execution Trace in your Streamlit application?**  
*Model Answer:* "In legal informatics, search engines cannot be black boxes. When a judge or advocate searches case law, they must verify why a case was retrieved. Our forensic execution trace logs the raw query, tokenization output, matching postings coordinates, and classifies retrieved documents into True Positives, False Positives, and False Negatives against ground truth, providing academic transparency."

**Q24: How does your system handle multilingual or vernacular terms common in Indian court judgments?**  
*Model Answer:* "Indian court judgments frequently incorporate vernacular legal terms from Hindi, Urdu, and regional languages (e.g., `panchnama`, `challan`, `kabala`, `talak`, `vakalatnama`). In our pipeline, conservative cleaning preserves non-ASCII tokens, and our 6,000-vocabulary BPE subword model segments unseen vernacular constructs into shared byte units, preventing out-of-vocabulary crashes."

**Q25: What is the single most important lesson from this project regarding generic vs. domain-specific NLP?**  
*Model Answer:* "Generic NLP pipelines make assumptions suited for news and social media—such as aggressive stopword removal and greedy suffix stripping. In domain-specific legal text, text normalization is inseparable from statutory reasoning. Protecting statutory citations as atomic units, shielding criminal negations, and using POS-guided lemmatization is not an optional optimization—it is essential for legal justice."

---
*Vidyashilp University · School of Advanced Computing · NLP Assessment 1 · 2026*
"""

    # Write Markdown file
    with open("reports/Observations_and_Viva_Questions.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    print("Created reports/Observations_and_Viva_Questions.md")

    # Build PDF using ReportLab
    pdf_filename = "reports/Observations_and_Viva_Questions.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0F172A") # Dark Navy
    accent_blue = colors.HexColor("#1D4ED8")   # Deep Blue
    accent_green = colors.HexColor("#047857")  # Forest Green
    text_dark = colors.HexColor("#1E293B")     # Slate Dark
    text_muted = colors.HexColor("#64748B")    # Slate Muted
    card_bg = colors.HexColor("#F8FAFC")       # Off White

    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=text_muted,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'H1',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=accent_blue,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        fontName='Helvetica',
        fontSize=8.8,
        leading=13,
        textColor=text_dark,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        fontName='Helvetica-Bold',
        fontSize=8.8,
        leading=13,
        textColor=primary_color,
        spaceAfter=4
    )

    qa_q_style = ParagraphStyle(
        'QA_Q',
        fontName='Helvetica-Bold',
        fontSize=9.2,
        leading=13.5,
        textColor=accent_blue,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    qa_a_style = ParagraphStyle(
        'QA_A',
        fontName='Helvetica',
        fontSize=8.6,
        leading=12.5,
        textColor=text_dark,
        spaceAfter=6
    )

    badge_style = ParagraphStyle(
        'Badge',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("Domain-Specific Text Analysis & Retrieval System for Indian Legal Judgments", title_style))
    story.append(Paragraph("<b>Individual Task Observations & Comprehensive Viva Defense Guide</b><br/>NLP Assessment 1 · Seventh Semester · School of Advanced Computing, Vidyashilp University", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=12))

    # Team Overview Table
    team_data = [
        [
            Paragraph("<b>Member</b>", body_bold),
            Paragraph("<b>Assigned Engineering Module</b>", body_bold),
            Paragraph("<b>Key Contribution & Technical Defense Focus</b>", body_bold)
        ],
        [
            Paragraph("<b>👤 Brunda</b>", body_style),
            Paragraph("Ingestion, Text Cleaning & Baseline Stemming", body_style),
            Paragraph("Ingested 25 court PDFs (257k tokens); conservative cleaning preserving ₹ and sub-clauses; empirical benchmark of Porter vs. Snowball vs. Lancaster.", body_style)
        ],
        [
            Paragraph("<b>👤 Shreerenu</b>", body_style),
            Paragraph("Stopwords, Baseline Pipeline A & Word Inverted Index", body_style),
            Paragraph("Engineered 8-term Protected Stopword Policy (49.9% compression); built word-level positional inverted index; mathematically proved over-stemming collisions (38.5% precision on 'executive').", body_style)
        ],
        [
            Paragraph("<b>👤 Lavanya</b>", body_style),
            Paragraph("Custom Legal Regex, ML POS Classifier & Legal NER", body_style),
            Paragraph("Engineered Custom Legal Regex Tokenizer (atomic citations); evaluated Penn Treebank failures; trained Supervised Logistic Regression POS Classifier (76.7% acc, 0.705 F1); Legal NER.", body_style)
        ],
        [
            Paragraph("<b>👤 Raju</b>", body_style),
            Paragraph("Contextual Lemmatization, Dual Index, IR Engine & Evaluation", body_style),
            Paragraph("Engineered POS contextual lemmatization (100% precision on collisions); built Dual-Level Atomic Positional Index (3.5× faster); Boolean & TF-IDF Cosine IR engine; 15-query evaluation win (+8.9% precision, +5.7% F1); Streamlit GUI.", body_style)
        ]
    ]

    t = Table(team_data, colWidths=[80, 150, 274])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    # PART 1: INDIVIDUAL OBSERVATIONS
    story.append(Paragraph("PART 1: INDIVIDUAL TASK OBSERVATIONS & EMPIRICAL FINDINGS", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#94A3B8"), spaceBefore=2, spaceAfter=8))

    # Brunda
    story.append(Paragraph("👤 Brunda: Observations on Ingestion, Cleaning & Stemming", h2_style))
    story.append(Paragraph("<b>1. OCR Line-Break Hyphenation:</b> Ingested 25 verified court judgments (257,849 tokens, 8,552 sentences). Court PDFs frequently contain broken words across line boundaries (e.g., <code>crimi-\\nnal</code>). Without proactive regex de-hyphenation, vocabulary counts artificially inflate, and queries for 'criminal' fail to match.", body_style))
    story.append(Paragraph("<b>2. Aggressive Cleaning Flaws:</b> Aggressive cleaning strips all non-alphanumerics, destroying Indian Rupee markers (<code>₹50,000/-</code> -> <code>50 000</code>) and deleting statutory sub-clause brackets (<code>Section 376(2)(i) IPC</code> -> <code>section 376 2 i ipc</code>). Deleting brackets destroys the aggravated statutory child rape threshold under the POCSO Act. Conservative cleaning preserves 100% of these statutory boundaries.", body_style))
    story.append(Paragraph("<b>3. Stemmer Evaluation (Why Porter over Snowball & Lancaster?):</b> Lancaster uses hyper-aggressive rules that destroy legal semantics: <code>legal</code> -> <code>leg</code>, <code>custody</code> -> <code>cust</code>, <code>bailment</code> -> <code>bail</code> (conflating contracts with criminal bail), and <code>appellants</code> -> <code>appl</code>. On our 257k tokens, Porter and Snowball produce 98.4% identical roots, and both fail on the exact same legal collisions (<code>execution</code>/<code>executive</code> both become <code>execut</code>). Porter was selected because it is the canonical, universally recognized baseline in IR benchmark literature (Manning et al., 2008), proving that suffix stripping itself is fundamentally inadequate.", body_style))
    story.append(Spacer(1, 6))

    # Shreerenu
    story.append(Paragraph("👤 Shreerenu: Observations on Stopwords, Pipeline A & Indexing", h2_style))
    story.append(Paragraph("<b>1. Liability Inversion:</b> Standard stopword lists discard negation words. In criminal law, stripping these words causes catastrophic inversion: <i>'applicant is not guilty'</i> becomes <code>['applicant', 'guilty']</code>, and <i>'no grounds for detention'</i> becomes <code>['grounds', 'detention']</code>. Queries for acquittal retrieve convictions, collapsing precision to 0%.", body_style))
    story.append(Paragraph("<b>2. 8-Term Protected Whitelist:</b> Whitelisted 8 critical terms: <code>not</code>, <code>no</code>, <code>never</code>, <code>without</code>, <code>unless</code>, <code>except</code>, <code>until</code>, <code>against</code>. This achieved a <b>49.9% corpus compression</b> (129,181 tokens retained from 257,849) while preserving 100% of criminal liability conditions.", body_style))
    story.append(Paragraph("<b>3. Inverted Index Structure & Stemmer Collisions:</b> Pipeline A indexes 8,355 unique stemmed terms with coordinate tuples <code>(sent_id, word_offset)</code>. We uncovered two fatal bottlenecks: (a) <code>execution</code> vs. <code>executive</code>: Both stem to <code>execut</code>, causing 8 false positives and plunging precision to <b>38.5%</b>. (b) <code>suit</code> vs. <code>suitable</code>: Both stem to <code>suit</code>, causing 7 false positives from employment cases and dropping precision to <b>58.8%</b>.", body_style))
    story.append(Spacer(1, 6))

    # Lavanya
    story.append(Paragraph("👤 Lavanya: Observations on Custom Tokenization, ML POS & NER", h2_style))
    story.append(Paragraph("<b>1. Custom Legal Regex:</b> Cascaded regex patterns preserve statutory citations (<code>Section 302 IPC</code>), constitutional articles (<code>Article 21</code>), rupee amounts (<code>₹50,000/-</code>), and Latin maxims (<code>suo motu</code>) as atomic single tokens, halving token counts from 10 to 5 on penal citations.", body_style))
    story.append(Paragraph("<b>2. Penn Treebank Syntax Errors:</b> Default NLTK POS taggers fail on court terms: <code>learned counsel</code> is tagged as a past verb (<code>VBD</code>) instead of adjective (<code>JJ</code>); <code>quashing</code> is tagged as participle (<code>VBG</code>) instead of remedy noun (<code>NN</code>); <code>ad-interim</code> is split into unknown punctuation.", body_style))
    story.append(Paragraph("<b>3. Supervised ML POS Classifier:</b> Trained a Multi-Class Logistic Regression model with L2 regularization using contextual n-gram features (suffixes 2-4, prefixes, title case, context words). Achieved <b>76.7% Test Accuracy</b> and <b>0.705 Weighted F1-Score</b> on held-out court text, successfully predicting <code>learned</code> as <code>JJ</code> (P=0.882) and <code>quashing</code> as <code>NN</code> (P=0.914).", body_style))
    story.append(Paragraph("<b>4. Legal NER & BPE Subwords:</b> Extracted 4 statutory entities (<code>LEGAL_SECTION</code>, <code>LEGAL_STATUTE</code>, <code>LEGAL_COURT</code>, <code>LEGAL_CITATION</code>). Trained 6,000-vocabulary BPE subwords segmenting rare words like <code>unconstitutional</code> into <code>un</code> + <code>constitution</code> + <code>al</code>.", body_style))
    story.append(Spacer(1, 6))

    # Raju
    story.append(Paragraph("👤 Raju: Observations on Lemmatization, Dual Index, IR Engine & Evaluation", h2_style))
    story.append(Paragraph("<b>1. Contextual Lemmatization Victory:</b> WordNet/spaCy lemmatizers guided by POS context preserve <code>execution</code> (noun) and <code>executive</code> (noun/adj) as distinct lemmas. Precision on the 'executive' query jumped from 38.5% in Pipeline A to <b>100.0% in Pipeline B</b> with zero false positives. Similarly, <code>suit</code> and <code>suitable</code> are kept distinct (100% precision).", body_style))
    story.append(Paragraph("<b>2. Dual-Level Indexing (3.5× Speedup):</b> Engineered a two-layer index (9,005 terms). Layer 1 indexes intact compound phrases (<code>'section 302 ipc'</code>). A query for this citation is a direct $O(1)$ hash table lookup, bypassing multi-word coordinate merges. Query latency dropped from 0.14 ms to <b>0.04 ms (3.5× faster!)</b>.", body_style))
    story.append(Paragraph("<b>3. Multi-Mode IR Engine:</b> Implemented Dijkstra's Shunting-Yard Boolean parser (supporting <code>AND</code>, <code>OR</code>, <code>NOT</code> and quoted phrases) and Vector Space TF-IDF Cosine similarity with length normalization.", body_style))
    story.append(Paragraph("<b>4. 15-Query Controlled Evaluation:</b> Pipeline B achieved <b>0.7721 Precision</b> (+8.9% over Pipeline A), <b>0.7979 F1-Score</b> (+5.7%), <b>0.8111 Precision@5</b> (+9.0%), and <b>0.04 ms latency</b>, while retaining 100% of the recall (0.8904). Pipeline B conclusively wins across all dimensions.", body_style))
    story.append(Spacer(1, 10))

    # Page Break for Viva Questions
    story.append(PageBreak())

    # PART 2: VIVA QUESTIONS
    story.append(Paragraph("PART 2: 25 COMPREHENSIVE VIVA QUESTIONS & MODEL ANSWERS", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#94A3B8"), spaceBefore=2, spaceAfter=8))

    qa_list = [
        # Brunda Qs
        ("Q1 (For Brunda): Why did you choose Conservative Cleaning over Aggressive Cleaning?",
         "Aggressive cleaning strips all non-alphanumerics. In Indian case law, this is disastrous: ₹50,000/- becomes '50 000' (erasing the rupee sign and splitting the number), and Section 376(2)(i) IPC becomes 'section 376 2 i ipc' (deleting parentheses that define the specific aggravated child rape clause under the POCSO Act harmonization). Conservative cleaning normalizes line-break hyphenations while strictly preserving statutory brackets, currency symbols, and quotes."),

        ("Q2 (For Brunda): What defect occurs when standard NLTK Word Tokenizer is used on legal citations?",
         "NLTK uses Penn Treebank regular expressions, treating periods, slashes, and spaces within citations as general word boundaries. It fragments 'Section 302 IPC' into ['Section', '302', 'IPC']. In downstream retrieval, a search for Section 302 will match any document containing 'Section' or '302' unless expensive positional coordinate merges are performed."),

        ("Q3 (For Brunda): Why did you reject the Lancaster Stemmer in favor of Porter?",
         "Lancaster uses hyper-aggressive, iterative replacement rules that mutilate legal morphology: 'legal' -> 'leg' (conflating law with the human body), 'custody' -> 'cust', 'bailment' -> 'bail' (conflating civil contracts under Indian Contract Act Section 148 with criminal surety bail), and 'appellants' -> 'appl'. Porter uses calibrated 5-step rules that preserve basic roots."),

        ("Q4 (For Brunda): If Snowball and Porter produce virtually identical stems, why pick Porter for Pipeline A?",
         "On our 257k legal tokens, Porter and Snowball produce 98.4% identical roots. Crucially, Snowball fails on the exact same legal polysemes as Porter—both collapse execution and executive to 'execut', and suit and suitable to 'suit'. Porter (1980) was chosen because it is the canonical, universally recognized baseline in IR literature (Manning et al., 2008), providing a recognized standard proving that suffix stripping itself is fundamentally inadequate."),

        ("Q5 (For Brunda): How did you handle OCR hyphenation errors across line wraps in court PDFs?",
         "Digital court PDFs often break words across line boundaries with hyphens (e.g. 'crimi-\\nnal'). In our conservative normalization pass, we used regular expression lookarounds to detect alphabetic tokens split by a hyphen and a newline character, recombining them into their intact single word ('criminal'). This prevented artificial vocabulary inflation and preserved token continuity."),

        # Shreerenu Qs
        ("Q6 (For Shreerenu): Why can't we use standard English stopword lists in criminal jurisprudence?",
         "Standard stopword lists remove negation words like not, no, without, unless, and against. In criminal law, stripping these words causes Catastrophic Liability Inversion: 'applicant is not guilty' becomes ['applicant', 'guilty'], and 'no grounds for detention' becomes ['grounds', 'detention']. A search for acquittal retrieves convictions! Precision collapses to 0% on negative condition queries."),

        ("Q7 (For Shreerenu): What is your Protected Stopword Policy and what compression did it achieve?",
         "Our policy whitelists 8 critical polarity and conditional operators: not, no, never, without, unless, except, until, against. Non-semantic filler words like 'the', 'is', 'at' are filtered out. Across our corpus, this reduced raw tokens from 257,849 to 129,181, achieving a 49.9% corpus compression while preserving 100% of criminal polarity conditions."),

        ("Q8 (For Shreerenu): Explain the data structure of your Word-Level Positional Inverted Index in Pipeline A.",
         "In Pipeline A, the index is a hash map where each key is a stemmed vocabulary term (8,355 unique stems). The value is a postings dictionary mapping each document ID to a list of coordinate tuples: (sentence_index, word_offset). For example, 'execut' maps to {'D08': [(14, 3), (42, 11)], 'D24': [(112, 7)]}. This allows verifying whether two stemmed words appear in adjacent positions."),

        ("Q9 (For Shreerenu): Explain the over-stemming collision in Pipeline A with the 'executive' query.",
         "The word 'execution' refers to decree enforcement under the CPC, while 'executive' refers to executive magistrates under the CrPC. Porter truncates both words to 'execut'. When a user searches for 'executive', Pipeline A loads postings for 'execut' and retrieves 13 judgments. Only 5 are true executive magistrate cases; 8 are civil decree executions. Precision collapses to 38.5%."),

        ("Q10 (For Shreerenu): Explain the second over-stemming collision in Pipeline A: 'suit' vs. 'suitable'.",
         "The legal noun 'suit' refers to civil title or partition lawsuits under the CPC, while 'suitable' is an ordinary English adjective used in employment or service jurisprudence. Porter strips both words to 'suit'. A search for 'suit' retrieves 17 judgments, 7 of which are employment or service disputes having nothing to do with civil suits, plunging precision to 58.8%."),

        # Lavanya Qs
        ("Q11 (For Lavanya): How does your Custom Legal Regex Tokenizer prevent citation fragmentation?",
         "Our tokenizer uses prioritized regular expression cascades that match entire statutory citations ('Section 302 IPC'), constitutional articles ('Article 21'), monetary conditions ('₹50,000/-'), and Latin maxims ('suo motu') before falling back to general word matching. For example, 'Bail under Section 438 CrPC of ₹50,000/-' is tokenized into 5 atomic tokens instead of 10 fragmented tokens."),

        ("Q12 (For Lavanya): Why does the Penn Treebank POS tagger fail on phrases like 'learned counsel'?",
         "Penn Treebank taggers were trained on the Wall Street Journal, where 'learned' functions as past tense verb 'to learn' (VBN/VBD). In judicial text, 'learned' is an honorific adjective (JJ) modifying counsel or judge. Our custom POS rules and ML classifier correctly classify it as JJ based on its syntactic position before legal nouns."),

        ("Q13 (For Lavanya): What features did you engineer for your Supervised ML POS Classifier?",
         "We engineered contextual n-gram features: character suffixes of length 2 to 4 (-ing, -tion, -able, -ed), prefixes (un-, non-), orthographic flags (is_title, is_upper, has_digit, has_hyphen), and preceding/following word tokens. We trained a Multi-Class Logistic Regression model with L2 regularization on Indian court text, achieving 76.7% Test Accuracy and 0.705 Weighted F1-Score."),

        ("Q14 (For Lavanya): What domain-specific entities does your Legal NER module extract?",
         "Our Legal NER module extracts four statutory domain entities: LEGAL_SECTION (Section 438 CrPC), LEGAL_STATUTE (NDPS Act, PMLA), LEGAL_COURT (Supreme Court of India), and LEGAL_CITATION (AIR 2020 SC 123). It also extracts standard entities: PERSON, ORG, MONEY, and GPE."),

        ("Q15 (For Lavanya): Why did you train a Byte Pair Encoding (BPE) model with a 6,000 vocabulary?",
         "Legal text contains complex morphological compounds, Latin prefixes, and hyphenated terms. Traditional word tokenizers replace unseen words with <UNK>. Our 6,000-vocabulary BPE model iteratively merges frequent character pairs, allowing rare words like 'unconstitutional' to be segmented into 'un' + 'constitution' + 'al', eliminating out-of-vocabulary loss."),

        # Raju Qs
        ("Q16 (For Raju): How does contextual lemmatization in Pipeline B resolve the 'executive' collision?",
         "Unlike stemmers that chop word endings using static suffix rules, WordNet and spaCy lemmatizers check morphological dictionaries conditioned on part-of-speech tags. Because our ML POS tagger tags 'execution' as a Noun and 'executive' as an Adjective/Noun, lemmatization preserves 'execution' and 'executive' as distinct dictionary lemmas. Querying 'executive' retrieves only the 5 true cases, achieving 100% precision with zero false positives."),

        ("Q17 (For Raju): Explain the Dual-Level Atomic Positional Index and why it is 3.5× faster.",
         "In Pipeline A, searching for 'Section 302 IPC' requires loading three separate postings lists ('section', '302', 'ipc') and running an iterative coordinate merge checking if pos(302) == pos(section) + 1. In Pipeline B, the index has two layers: Layer 1 indexes intact compound phrases ('section 302 ipc') directly. A search for this citation is a single O(1) hash table lookup. Layer 2 indexes constituent lemmas for single-word queries. This direct lookup reduced query latency from 0.14 ms to 0.04 ms (3.5× faster)."),

        ("Q18 (For Raju): How does your Boolean Retrieval Engine parse queries like '\"anticipatory bail\" AND NOT murder'?",
         "We implemented Dijkstra's Shunting-Yard algorithm to convert infix Boolean queries into Reverse Polish Notation (postfix). Operator precedence is enforced: NOT > AND > OR. Quoted phrases are treated as atomic tokens. The engine evaluates the postfix stack using set operations: it computes the intersection of postings for 'anticipatory bail' and takes the set difference with postings for 'murder'."),

        ("Q19 (For Raju): Explain the mathematical formula for your Vector Space TF-IDF Cosine Retrieval.",
         "We compute sublinear term frequency: TF(t,d) = 1 + log(TF_t,d) for TF > 0. The inverse document frequency is IDF(t) = log(N / DF_t), where N=25. The query-document score is the cosine angle normalized against Euclidean document length: Score(q,d) = (sum TF-IDF(t,d)*TF-IDF(t,q)) / (||d|| * ||q||). Length normalization eliminates bias toward lengthy High Court judgments."),

        ("Q20 (For Raju): Walk us through the 15-query benchmark evaluation. Why is Pipeline B the winning model?",
         "Across 15 legal benchmark queries, Pipeline B achieved Mean Precision of 0.7721 vs. 0.7089 (+8.9% gain), Mean Recall of 0.8904 vs. 0.8904 (100% recall retained), Mean F1-Score of 0.7979 vs. 0.7549 (+5.7% harmonic gain), Precision@5 of 0.8111 vs. 0.7444 (+9.0%), and Latency of 0.04 ms vs. 0.14 ms (3.5× faster). Pipeline B decisively wins because it eliminates false positives without sacrificing a single point of recall."),

        # Cross-Cutting Qs
        ("Q21 (All Members): Why did Pipeline B improve Precision WITHOUT dropping Recall?",
         "In traditional IR, precision is boosted by narrowing search criteria, which often drops recall by excluding borderline cases. In our legal domain, however, Pipeline A's low precision was caused by artificial false positives from stemmer collisions ('execut' matching decree cases) and fragmented citations. Pipeline B eliminated linguistic false positives through POS-aware lemmatization and atomic citation preservation while retaining all true relevant documents, thereby preserving 100% of the recall (0.8904)."),

        ("Q22 (All Members): How would your system scale if the corpus grew from 25 judgments to 100,000 judgments?",
         "Currently, our postings lists reside in in-memory Python dictionaries with JSON persistence. At 100,000 documents: (1) We would migrate from in-memory hash maps to disk-based inverted indexes using Block Sort-Based Indexing (BSBI) or Single-Pass In-Memory Indexing (SPIMI). (2) We would compress postings lists using Variable Byte (Varint) or Elias-Gamma gap encoding. (3) Layer 1 atomic compound indexing would be limited to statutory entities extracted by NER to prevent vocabulary explosion."),

        ("Q23 (All Members): What is the significance of the Forensic IR Execution Trace in your Streamlit application?",
         "In legal informatics, search engines cannot be black boxes. When a judge or advocate searches case law, they must verify why a case was retrieved. Our forensic execution trace logs the raw query, tokenization output, matching postings coordinates, and classifies retrieved documents into True Positives, False Positives, and False Negatives against ground truth, providing academic transparency."),

        ("Q24 (All Members): How does your system handle multilingual or vernacular terms common in Indian court judgments?",
         "Indian court judgments frequently incorporate vernacular legal terms from Hindi, Urdu, and regional languages (e.g., panchnama, challan, kabala, talak, vakalatnama). In our pipeline, conservative cleaning preserves non-ASCII tokens, and our 6,000-vocabulary BPE subword model segments unseen vernacular constructs into shared byte units, preventing out-of-vocabulary crashes."),

        ("Q25 (All Members): What is the single most important lesson from this project regarding generic vs. domain-specific NLP?",
         "Generic NLP pipelines make assumptions suited for news and social media—such as aggressive stopword removal and greedy suffix stripping. In domain-specific legal text, text normalization is inseparable from statutory reasoning. Protecting statutory citations as atomic units, shielding criminal negations, and using POS-guided lemmatization is not an optional optimization—it is essential for legal justice.")
    ]

    for q_text, a_text in qa_list:
        story.append(Paragraph(q_text, qa_q_style))
        story.append(Paragraph(f"<b>Model Answer:</b> {a_text}", qa_a_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully compiled {pdf_filename} via ReportLab!")

if __name__ == "__main__":
    build_pdf_and_md()
