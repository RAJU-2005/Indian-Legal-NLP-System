# NLP Assessment 1: Individual Task Observations & Viva Defense Guide
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
1. **Corpus Ingestion & OCR Line-Break Hyphenation:** Ingested 25 full-text digital PDF judgments (257,849 tokens, 8,552 sentences) from the Supreme Court and 6 High Courts. A primary observation was that scanned and court-formatted PDFs frequently contain broken words across line breaks (e.g., `crimi-\nnal`, `prose-\ncution`). Without proactive de-hyphenation, vocabulary counts artificially inflate, and search queries for "criminal" fail to match words broken across line wraps.
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
   - *Vector Space TF-IDF Cosine Retrieval:* Implemented sublinear term frequency scoring $	ext{TF-IDF}(t,d) = (1 + \log 	ext{TF}_{t,d}) 	imes \log(N/	ext{DF}_t)$ normalized against Euclidean document length.
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
*Model Answer:* "Digital court PDFs often break words across line boundaries with hyphens, such as `crimi-\nnal` or `prose-\ncution`. In our conservative normalization pass, we used regular expression lookarounds to detect alphabetic tokens split by a hyphen and a newline character, recombining them into their intact single word (`criminal`, `prosecution`). This prevented artificial vocabulary inflation and preserved token continuity."

---

### 🎤 Category 2: Questions for Shreerenu (Stopwords, Inverted Index & Pipeline A)

**Q6: Why can't we use standard English stopword lists in criminal jurisprudence?**  
*Model Answer:* "Standard stopword lists remove negation words like `not`, `no`, `without`, `unless`, and `against`. In criminal law, stripping these words causes Catastrophic Liability Inversion. For instance, `"the applicant is not guilty"` is stripped to `['applicant', 'guilty']`, and `"no offence is made out"` becomes `['offence', 'made']`. A search for judgments of acquittal retrieves judgments of conviction! Precision collapses to 0% on negative condition queries."

**Q7: What is your Protected Stopword Policy and what corpus compression did it achieve?**  
*Model Answer:* "Our policy whitelists 8 critical polarity and conditional operators: `not`, `no`, `never`, `without`, `unless`, `except`, `until`, and `against`. Non-semantic filler words like `the`, `is`, `at`, and `wherein` are filtered out. Across our corpus, this reduced raw tokens from 257,849 to 129,181, achieving a **49.9% corpus compression** while preserving 100% of criminal polarity conditions."

**Q8: Explain the data structure of your Word-Level Positional Inverted Index in Pipeline A.**  
*Model Answer:* "In Pipeline A, the index is a hash map where each key is a stemmed vocabulary term (8,355 unique stems). The value is a postings dictionary mapping each document ID to a list of coordinate tuples: `(sentence_index, word_offset)`. For example, `execut` maps to `{'D08': [(14, 3), (42, 11)], 'D24': [(112, 7)]}`. This allows verifying whether two stemmed words appear in adjacent positions."

**Q9: Explain the over-stemming collision in Pipeline A with the 'executive' query.**  
*Model Answer:* "The word `execution` refers to decree enforcement under the Code of Civil Procedure, while `executive` refers to executive magistrates under the CrPC. The Porter stemmer truncates both words to `execut`. When a user searches for `"executive"`, Pipeline A loads the postings for `execut` and retrieves 13 judgments. Only 5 are true executive magistrate cases; 8 are civil decree executions. Precision collapses to **38.5%**."

**Q10: Explain the second over-stemming collision in Pipeline A: 'suit' vs. 'suitable'.**  
*Model Answer:* "The legal noun `suit` refers to civil title or partition lawsuits under the CPC, while `suitable` is an ordinary English adjective used in employment or service jurisprudence (e.g., 'suitable accommodation', 'suitable candidate'). Porter strips both words to `suit`. A search for `"suit"` retrieves 17 judgments, 7 of which are employment or service disputes having nothing to do with civil suits, plunging precision to **58.8%**."

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
*Model Answer:* "Unlike stemmers that chop word endings using static suffix rules, WordNet and spaCy lemmatizers check morphological dictionaries conditioned on part-of-speech tags. Because our ML POS tagger tags `execution` as a Noun and `executive` as an Adjective/Noun, lemmatization preserves `execution` and `executive` as distinct dictionary lemmas. Querying `"executive"` retrieves only the 5 true cases, achieving **100% precision** with zero false positives."

**Q17: Explain the Dual-Level Atomic Positional Index and why it is 3.5× faster.**  
*Model Answer:* "In Pipeline A, searching for `Section 302 IPC` requires loading three separate postings lists (`section`, `302`, `ipc`) and running an iterative coordinate merge checking if `pos(302) == pos(section) + 1`. In Pipeline B, the index has two layers: Layer 1 indexes intact compound phrases (`'section 302 ipc'`) directly. A search for this citation is a single $O(1)$ hash table lookup. Layer 2 indexes constituent lemmas for single-word queries. This direct lookup reduced query latency from 0.14 ms to **0.04 ms (3.5× faster)**."

**Q18: How does your Boolean Retrieval Engine parse queries like '"anticipatory bail" AND NOT murder'?**  
*Model Answer:* "We implemented Dijkstra's Shunting-Yard algorithm to convert infix Boolean queries into Reverse Polish Notation (postfix). Operator precedence is enforced: `NOT` has highest precedence, followed by `AND`, followed by `OR`. Quoted phrases are treated as atomic tokens. The engine evaluates the postfix stack using set operations: it computes the intersection of postings for `anticipatory bail` and takes the set difference with postings for `murder`."

**Q19: Explain the mathematical formula for your Vector Space TF-IDF Cosine Retrieval.**  
*Model Answer:* "We compute sublinear term frequency: $	ext{TF}(t,d) = 1 + \log(	ext{TF}_{t,d})$ for $	ext{TF} > 0$. The inverse document frequency is $	ext{IDF}(t) = \log(N / 	ext{DF}_t)$, where $N=25$. The query-document score is the cosine angle:
$$	ext{Score}(q, d) = rac{\sum_{t \in q} 	ext{TF-IDF}(t,d) \cdot 	ext{TF-IDF}(t,q)}{\sqrt{\sum_{t \in d} 	ext{TF-IDF}(t,d)^2} \cdot \sqrt{\sum_{t \in q} 	ext{TF-IDF}(t,q)^2}}$$
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
