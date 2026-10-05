================================================================================
NLP ASSESSMENT 1: DOMAIN-SPECIFIC TEXT ANALYSIS & RETRIEVAL SYSTEM FOR INDIAN LEGAL JUDGMENTS
COMPLETE SPOKEN PRESENTATION SCRIPT & VIVA DEFENSE GUIDE
================================================================================

Course: Natural Language Processing (Assessment 1, Seventh Semester)
Institution: School of Advanced Computing, Vidyashilp University
Format: Single Interactive HTML Slide Deck (reports/Presentation.html) - 25 Slides
Team Structure & Member Roles:
  1. Brunda    (Slides 1-6)   : Raw Ingestion, Text Cleaning, Baseline Tokenization & Stemming
  2. Shreerenu (Slides 7-12)  : Stopword Polarity, Pipeline A Architecture, Positional Index & Collisions
  3. Lavanya   (Slides 13-18) : Custom Legal Regex Tokenizer, ML POS Classifier & Legal NER
  4. Raju      (Slides 19-24) : Contextual Lemmatization, Dual-Level Index, IR Engine, Evaluation & GUI Demo
  All Members  (Slide 25)     : Conclusion, Verdict & Viva Defense Handling

================================================================================
TABLE OF CONTENTS & PRESENTATION FLOW
================================================================================
Slides 1–6   | Brunda    | Foundations, 25 PDFs, Normalization, Tokenization & Stemmer Experiments
Slides 7–12  | Shreerenu | Stopword Polarity, Pipeline A, Positional Index & Stemmer Collisions
Slides 13–18 | Lavanya   | Custom Legal Regex, Penn Treebank Errors, Supervised ML POS & Legal NER
Slides 19–24 | Raju      | Contextual Lemmatization, Dual-Level Index, Multi-Mode IR & 15-Query Evaluation
Slide 25     | All       | Synthesis, Conclusion, Final Model Selection & Viva Defense

================================================================================
SECTION 1: FOUNDATIONS & INGESTION (Brunda Speaks — Slides 1 to 6)
================================================================================

--------------------------------------------------------------------------------
SLIDE 1: Title Slide & Team Introduction
--------------------------------------------------------------------------------
[Brunda Speaks]:
"Good morning Ma'am and esteemed faculty. Today, our team is presenting our NLP Assessment 1 project: 'A Domain-Specific Text Analysis and Retrieval System for Indian Legal Judgments'.

In compliance with the assignment framework of Select -> Order -> Implement -> Compare -> Evaluate -> Justify, we have designed, implemented, and empirically compared two end-to-end NLP retrieval pipelines across 25 authoritative Supreme Court and High Court judgments.

We are a team of four members, and our work is divided into two specialized engineering sub-teams:
  - Myself (Brunda): I led the raw dataset ingestion, domain-aware text cleaning, and baseline tokenization and stemmer benchmarking.
  - Shreerenu: Engineered our stopword polarity policy, architected baseline Pipeline A, and implemented its word-level positional inverted index.
  - Lavanya: Developed the domain adaptations for Pipeline B, including our Custom Legal Regex Tokenizer, Supervised ML POS Classifier, and Legal Named Entity Recognition.
  - Raju: Engineered contextual lemmatization, built the dual-level atomic index, constructed the multi-mode retrieval engine, conducted the 15-query benchmark evaluation, and will demonstrate our live Streamlit GUI.

Let us begin with the core problem that motivated this project."

--------------------------------------------------------------------------------
SLIDE 2: Why Generic Off-the-Shelf NLP Fails on Indian Case Law
--------------------------------------------------------------------------------
[Brunda Speaks]:
"Ma'am, in legal informatics, we cannot treat court judgments like general news articles or social media posts. Judicial rulings contain precise statutory reasoning, penal clauses, and constitutional doctrines where single words dictate personal liberty and criminal liability.

When standard, general-purpose NLP pipelines are applied to Indian court judgments without domain adaptation, they break down in three major ways. Here are three concrete project examples for each failure mode:

1. Citation Fragmentation:
   - Example 1: 'Section 302 IPC' -> standard tokenizers split this into ['Section', '302', 'IPC']. This destroys the compound penal entity, causing search queries to match any unrelated section number in the corpus.
   - Example 2: 'Article 21 of Constitution' -> shattered into ['Article', '21', 'of', 'Constitution'], dispersing the fundamental right against unlawful detention.
   - Example 3: '₹50,000/- bail bond' -> fragmented into isolated punctuation and digits ['₹', '50', ',', '000', '/', '-'], completely obliterating the monetary threshold.

2. Semantic Liability Inversion:
   - Example 1: 'The applicant is not guilty' -> standard stopword filters discard 'not', leaving ['applicant', 'guilty']. This inverts complete innocence into criminal guilt!
   - Example 2: 'Without reasonable doubt' -> stripped to ['reasonable', 'doubt'], reversing the prosecution's evidentiary threshold.
   - Example 3: 'No grounds for detention' -> stripped to ['grounds', 'detention'], turning a judicial release order into unlawful justification for imprisonment.

3. Over-Stemming Collisions:
   - Example 1: 'execution' (of a civil money decree) and 'executive' (magistrate authority) -> algorithmic stemmers truncate both to 'execut', causing 8 false positives in search results!
   - Example 2: 'suit' (civil title lawsuit) and 'suitable' (appropriate candidate) -> both collapse to 'suit', polluting property litigation searches with employment adjectives!
   - Example 3: 'custody' (police/judicial remand) and 'custodian' (property trustee) -> Lancaster truncates to 'cust', obliterating legal meaning.

Our objective was to scientifically document these failures in Pipeline A and eliminate them in Pipeline B."

--------------------------------------------------------------------------------
SLIDE 3: Authoritative Corpus Architecture & Domain-Aware Normalization
--------------------------------------------------------------------------------
[Brunda Speaks]:
"Here is our dataset. In accordance with the assignment requirement of at least 15 domain-specific documents, we ingested 25 verified digital PDF judgments from the Indian Supreme Court and High Courts (Allahabad, Bombay, Calcutta, Delhi, Karnataka, and Patna).

We established a deterministic mapping between PDF files and document IDs D01 through D25 based on the instructor's Excel metadata. Across these 25 judgments, our corpus covers six major legal sectors: Cybercrime & IT Act (D01–D05), Economic Offenses/PMLA (D06–D08), Narcotics NDPS Act (D09–D10), Homicide IPC 302 (D11–D13), Matrimonial/Dowry Death (D14–D15), and Preventive Detention under Habeas Corpus (D21–D22).

Empirically, our corpus comprises:
  - 25 Verified Judgments
  - 257,849 Total Tokens
  - 8,552 Sentences
  - 10,819 Unique Vocabulary Terms

Crucially, to keep normalization domain-aware, we engineered four specific techniques:
  1. Statutory Case-Folding: Standardizing running text to lowercase while shielding statutory uppercase acronyms (IPC, CrPC, AIR, SCC, NDPS) so legal authority is not degraded.
  2. Line-Break De-Hyphenation: Normalizing OCR split words across line wraps (e.g., 'crimi-\nnal' -> 'criminal', 'prose-\ncution' -> 'prosecution').
  3. Quotation & Latin Maxim Retention: Preserving double quotation marks ('"..."') and Latin doctrines ('mens rea', 'suo motu', 'ultra vires', 'habeas corpus') for exact phrase matching.
  4. Sub-Clause Punctuation Protection: Retaining parentheses in statutory sub-clauses ('Section 376(2)(i)') and Indian Rupee markers ('₹50,000/-')."

--------------------------------------------------------------------------------
SLIDE 4: Conservative vs. Aggressive Text Cleaning
--------------------------------------------------------------------------------
[Brunda Speaks]:
"In Module 1, we compared two text cleaning paradigms: Aggressive Cleaning versus Conservative Cleaning.

In general NLP, practitioners aggressively strip all punctuation, brackets, and non-alphanumeric symbols. But in Indian case law, aggressive cleaning is destructive:
  - Aggressive Example 1: '₹50,000/-' becomes '50 000'. The currency symbol is destroyed, and the number is fragmented into two meaningless pieces.
  - Aggressive Example 2: 'Section 376(2)(i) IPC' becomes 'section 376 2 i ipc'. Stripping the brackets destroys the specific penal subsection governing aggravated sexual assault under the POCSO harmonization framework.

Therefore, I engineered a Conservative Text Normalization routine. It standardizes whitespace, repairs OCR line breaks, and preserves statutory clause brackets, quotation boundaries, currency symbols, and hyphenated legal compounds like 'non-bailable' and 'suo-motu'. This preserved 100% of the statutory and financial thresholds across all 25 PDF extractions."

--------------------------------------------------------------------------------
SLIDE 5: Conventional Tokenization & Citation Splitting (5 Project Examples)
--------------------------------------------------------------------------------
[Brunda Speaks]:
"Next, in Module 2, I benchmarked conventional tokenization. Standard Whitespace tokenization preserves character chunks but leaves attached punctuation, which pollutes vocabulary keys.

Meanwhile, standard NLTK Word Tokenization, which uses Penn Treebank regular expressions, fragments legal citations. Here are five real examples from our project corpus:
  1. 'Section 302 IPC' -> ['Section', '302', 'IPC'] (Splits penal unit into 3 pieces; searches match any section).
  2. 'bail bond of ₹50,000/-' -> ['bail', 'bond', 'of', '₹', '50,000', '/', '-'] (Splits monetary fine and bond threshold into 4 isolated tokens).
  3. 'writ of habeas corpus' -> ['writ', 'of', 'habeas', 'corpus'] (Splits Latin constitutional writ; 'habeas' has zero independent legal meaning).
  4. 'Section 376(2)(i) IPC' -> ['Section', '376', '(', '2', ')', '(', 'i', ')', 'IPC'] (Parentheses stripped; destroys specific aggravated child rape clause).
  5. 'AIR 2020 SC 1450' -> ['AIR', '2020', 'SC', '1450'] (Fragments All India Reporter case law citation into arbitrary numbers and initials).

My finding: Conventional tokenizers treat punctuation within legal citations as general word boundaries, forcing downstream retrieval in Pipeline A to perform expensive multi-word positional merges!"

--------------------------------------------------------------------------------
SLIDE 6: Stemming Experiments: Porter vs. Snowball vs. Lancaster
--------------------------------------------------------------------------------
[Brunda Speaks]:
"For morphological stemming in baseline Pipeline A, examiners frequently probe two critical questions:
First: Why was Lancaster rejected?
Look at the table on the left: Lancaster uses hyper-aggressive, iterative replacement rules that mutilate legal morphology:
  - 'legal' -> 'leg' (conflating the legal profession with an anatomical human leg!)
  - 'custody' -> 'cust' (truncated into unsearchable noise)
  - 'bailment' -> 'bail' (a fatal cross-domain error: conflating civil contract bailment under Section 148 of the Indian Contract Act with criminal surety bail under the CrPC!)
  - 'appellants' -> 'appl' (conflating court litigants with an apple or an application!)
This causes severe false-positive pollution, making Lancaster completely unusable for legal retrieval.

Second: Why did we pick Porter over Snowball?
Snowball is often called 'Porter 2', so why not use Snowball?
  1. Empirical Equivalence: Across all 257,849 tokens in our 25 judgments, Porter and Snowball produce 98.4% identical roots.
  2. Shared Suffix Blindness: Snowball was designed to handle irregular modern conversational English (like trailing '-ly' and '-e' suffixes)—it has zero semantic awareness of domain polysemes. Consequently, Snowball still suffers from the exact same fatal collisions: both Porter and Snowball collapse 'execution' and 'executive' to 'execut', and both collapse 'suit' and 'suitable' to 'suit'!
  3. Canonical Academic Standard: Porter (1980) is the universally recognized baseline in IR benchmark literature (Manning et al., 2008). Using Porter establishes an authoritative baseline that proves algorithmic suffix stripping itself is fundamentally flawed for law, directly motivating our shift to Contextual POS Lemmatization in Pipeline B!

I now hand over to Shreerenu to present stopwords and Pipeline A."

================================================================================
SECTION 2: BASELINE PIPELINE A & INDEXING (Shreerenu Speaks — Slides 7 to 12)
================================================================================

--------------------------------------------------------------------------------
SLIDE 7: Stopwords & The Catastrophic Inversion of Liability
--------------------------------------------------------------------------------
[Shreerenu Speaks]:
"Thank you Brunda. I am Shreerenu. In Module 2, I analyzed stopword filtering and architected baseline Pipeline A.

In general NLP, standard stopword lists contain 179 high-frequency English words like 'the', 'is', 'at', 'not', and 'no'. In general text, dropping these words is harmless. But in criminal jurisprudence, this causes Catastrophic Liability Inversion:
  - 'Applicant is not guilty' -> becomes ['applicant', 'guilty']!
  - 'Order passed without jurisdiction' -> becomes ['order', 'passed', 'jurisdiction']!
  - 'No offence made out' -> becomes ['offence', 'made']!

If a legal researcher searches for judgments where an accused was 'not guilty', dropping negation words forces the engine to retrieve cases where the accused was found 'guilty'! Precision collapses to 0% on negative condition queries."

--------------------------------------------------------------------------------
SLIDE 8: The Protected Legal Stopword Policy
--------------------------------------------------------------------------------
[Shreerenu Speaks]:
"To resolve this, I formulated our Protected Legal Stopword Policy. We created a strict negation whitelist protecting 8 critical polarity and conditional operators:
  'not', 'no', 'never', 'without', 'unless', 'except', 'until', 'against'.

All non-semantic fluff ('the', 'is', 'wherein', 'hereto') is filtered out, but these 8 terms are shielded.

Empirical Results across our corpus:
  - Raw Tokens: 257,849
  - Retained Tokens: 129,181
  - Corpus Compression: 49.9% reduction!

Design Decision: Both Pipeline A and Pipeline B incorporate this protected negation whitelist so that our comparative evaluation reflects morphological and tokenization differences, rather than simple polarity errors."

--------------------------------------------------------------------------------
SLIDE 9: Pipeline A: Conventional Baseline Architecture
--------------------------------------------------------------------------------
[Shreerenu Speaks]:
"Here is the complete architectural flowchart of Pipeline A that I orchestrated.

Raw PDF judgments flow through:
  1. Conservative Text Cleaning
  2. Conventional Tokenization (Standard NLTK Word Tokenizer)
  3. Protected Stopword Removal
  4. Morphological Stemming (Porter Stemmer)
  5. Positional Inverted Indexing
  6. Information Retrieval Engine

Notice our clean architecture diagram with embedded failure callouts:
  - At Tokenization: Citation fragmentation splits 'Section 302 IPC' into 3 isolated tokens.
  - At Stemming: Exactly one critical red callout: Over-stemming collision collapses 'execution' and 'executive' to 'execut', causing 8 false positives and plunging precision to 38.5%!
  - At Indexing & IR: Quoted phrases require expensive iterative coordinate joins."

--------------------------------------------------------------------------------
SLIDE 10: Pipeline A: Word-Level Positional Inverted Index
--------------------------------------------------------------------------------
[Shreerenu Speaks]:
"To enable multi-word phrase matching, I implemented a Word-Level Positional Inverted Index.

Postings Data Structure:
Each stemmed vocabulary term maps to a dictionary of document IDs, where each entry contains a list of coordinate tuples: sentence index and token word offset.
For example, the stem 'execut' maps to:
  'D08': [(s:14, w:3), (s:42, w:11)],
  'D14': [(s:5, w:12)],
  'D24': [(s:112, w:7), (s:115, w:2)]

Index Metrics:
  - Indexed Vocabulary: 8,355 unique stemmed terms.
  - Storage: In-memory Python hash map with persistent JSON serialization.
  - Average Latency: 0.14 ms per query.

This index allows us to verify adjacency for phrase queries."

--------------------------------------------------------------------------------
SLIDE 11: Phrase Matching via Positional Coordinate Merge
--------------------------------------------------------------------------------
[Shreerenu Speaks]:
"Here is how phrase matching works in Pipeline A using Positional Coordinate Merge.

When a user searches for '"anticipatory bail"':
  1. The query terms are stemmed to 'anticipatori' and 'bail'.
  2. The engine loads the postings list for 'anticipatori' in D07: offsets [45, 112, 230].
  3. The engine loads the postings list for 'bail' in D07: offsets [46, 89, 113, 231].
  4. The algorithm performs an adjacency check: does offset(bail) equal offset(anticipatori) + 1?
     - 45 + 1 = 46 (Match!)
     - 112 + 1 = 113 (Match!)
     - 230 + 1 = 231 (Match!)
  5. Document D07 is verified as containing the exact phrase!

The Architectural Bottleneck:
This requires loading multiple postings lists and executing an O(N+M) coordinate merge for every phrase query, increasing latency and memory bandwidth."

--------------------------------------------------------------------------------
SLIDE 12: The Over-Stemming Bottlenecks in Pipeline A: Two Failure Cases
--------------------------------------------------------------------------------
[Shreerenu Speaks]:
"Now, look at the critical vulnerability I uncovered in Pipeline A: Algorithmic Over-Stemming Collisions. We document two major failure cases from our corpus:

Bottleneck 1: 'execution' vs. 'executive' -> 'execut'
  - Legal Concept 1: Enforcement of a civil money decree or death warrant.
  - Legal Concept 2: Executive magistrate or administrative detention under CrPC.
  - When a user searches for 'executive', Pipeline A stems the query to 'execut' and retrieves 13 judgments!
  - Only 5 are true executive magistrate cases (D09, D14, D18, D20, D23).
  - 8 judgments are false positives dealing with civil decree execution (D24, D25, D01)!
  - Precision collapses to 38.5%!

Bottleneck 2: 'suit' vs. 'suitable' -> 'suit'
  - Legal Concept 1: Civil partition lawsuit or money suit under the Code of Civil Procedure.
  - Legal Concept 2: General English adjective 'suitable' (e.g., 'suitable accommodation', 'suitable candidate' in employment).
  - When a user searches for 'suit', Pipeline A retrieves 17 judgments. 7 judgments are false positives from service and employment rulings!
  - Precision drops to 58.8%!

I now hand over to Lavanya to present our domain NLP innovations for Pipeline B."

================================================================================
SECTION 3: DOMAIN NLP INNOVATIONS (Lavanya Speaks — Slides 13 to 18)
================================================================================

--------------------------------------------------------------------------------
SLIDE 13: The Solution: Legal-Domain-Optimized Architecture
--------------------------------------------------------------------------------
[Lavanya Speaks]:
"Hello Ma'am. I am Lavanya. Seeing the failure points identified by Brunda and Shreerenu—citation fragmentation, POS tagging errors, and over-stemming—I developed the domain NLP components for Pipeline B:
  1. Custom Legal Regex Tokenizer
  2. Supervised ML Logistic Regression POS Classifier
  3. Legal Named Entity Recognition
  4. Higher-Order N-Grams and BPE Subwords

Our engineering philosophy was: 'Preserve legal semantics at the token level, eliminating expensive downstream repairs.' Let us inspect each innovation."

--------------------------------------------------------------------------------
SLIDE 14: Custom Legal Regular Expressions (Pipeline B)
--------------------------------------------------------------------------------
[Lavanya Speaks]:
"To fix citation fragmentation, I built a Custom Legal Regex Tokenizer using prioritized regex patterns:
  - Sections: (?:Section|Sec\.|Article|Art\.)\s+\d+[A-Z]?(?:\(\d+\))*
  - Monetary: (?:₹|Rs\.?)\s*[\d,]+(?:\/-)?
  - Latin Maxims: (?i)\b(?:suo\s+motu|mens\s+rea|habeas\s+corpus|prima\s+facie)\b
  - Statutes: (?:IPC|CrPC|CPC|NDPS|PMLA|NIA|POCSO|IT\s+Act)

Look at the tokenization comparison on: 'Bail under Section 438 CrPC of ₹50,000/-':
  - Pipeline A (NLTK) produces 10 fragmented tokens: ['Bail', 'under', 'Section', '438', 'CrPC', 'of', '₹', '50,000', '/', '-']
  - Pipeline B (Custom Regex) produces 5 clean, atomic tokens: ['Bail', 'under', 'Section 438 CrPC', 'of', '₹50,000/-']!

By keeping statutory sections and monetary thresholds intact as single tokens, we preserve legal semantics directly at the token level."

--------------------------------------------------------------------------------
SLIDE 15: Penn Treebank Syntax Failures vs. Custom Legal POS Tagging
--------------------------------------------------------------------------------
[Lavanya Speaks]:
"Next, I investigated part-of-speech tagging. Standard Penn Treebank POS taggers are trained on the Wall Street Journal, causing severe errors on Indian judicial text.

Here are five real corpus examples verified against their Ground Truth legal syntactic roles:
  1. 'The learned counsel argued...'
     - NLTK Default: 'learned' tagged as VBN (Past Verb) [ERROR]
     - Custom Legal POS: JJ (Adjective) [CORRECT]
     - Ground Truth: Honorific Adjective modifying judicial counsel.
  2. 'Petitioner sought quashing of FIR'
     - NLTK Default: 'quashing' tagged as VBG (Participle Verb) [ERROR]
     - Custom Legal POS: NN (Noun) [CORRECT]
     - Ground Truth: Substantive Legal Remedy Noun under Section 482 CrPC.
  3. 'Court took suo motu cognizance'
     - NLTK Default: 'suo' tagged as NN (Noun) [ERROR]
     - Custom Legal POS: RB (Adverb) [CORRECT]
     - Ground Truth: Adverbial Motion Modifier ('on its own motion').
  4. 'The bench dismissed appeal'
     - NLTK Default: 'bench' tagged as NN (Furniture/Seat) [ERROR]
     - Custom Legal POS: NNP (Judicial Panel) [CORRECT]
     - Ground Truth: Judicial Institution / Division Bench.
  5. 'Granted ad-interim bail'
     - NLTK Default: 'ad-interim' split into unknown punctuation [ERROR]
     - Custom Legal POS: JJ (Adjective) [CORRECT]
     - Ground Truth: Interlocutory Order Modifier."

--------------------------------------------------------------------------------
SLIDE 16: Supervised ML POS Classifier: 3 Real Legal Case Results
--------------------------------------------------------------------------------
[Lavanya Speaks]:
"Beyond rule-based tagging, I trained a Supervised Machine Learning POS Classifier using Multi-Class Logistic Regression with L2 regularization.

I engineered rich contextual features: character suffixes of length 2 to 4 (capturing -ing, -tion, -able), prefixes (un-, non-), orthographic flags (is_title, has_digit), and preceding/following context words.

Here are three real project classification results:
  - Case 1: 'The learned counsel for appellant'
    Features: word[-2:]='ed', next='counsel', prev='The'
    Penn Treebank tagged VBD -> Our ML Classifier predicted JJ (Adjective, P=0.882) -> Correct!
  - Case 2: 'remedy of quashing of FIR'
    Features: word[-3:]='ing', next='of', prev='remedy'
    Penn Treebank tagged VBG -> Our ML Classifier predicted NN (Noun, P=0.914) -> Correct!
  - Case 3: 'grant of ad-interim injunction'
    Features: has_hyphen=True, next='injunction'
    Penn Treebank split -> Our ML Classifier predicted JJ (Adjective, P=0.847) -> Correct!

Held-out Empirical Evaluation:
On a 20% held-out test split of annotated court sentences, our ML POS Classifier achieved 76.7% Test Accuracy and a 0.705 Weighted F1-Score!"

--------------------------------------------------------------------------------
SLIDE 17: Named Entity Recognition in Indian Case Law
--------------------------------------------------------------------------------
[Lavanya Speaks]:
"I also implemented domain-specific Named Entity Recognition. Legal text requires identifying specialized legal categories alongside standard linguistic entities.

Our NER pipeline extracts:
  - LEGAL_SECTION: Section 438 CrPC, Section 302 IPC, s. 135 Customs
  - LEGAL_STATUTE: Code of Criminal Procedure, NDPS Act, PMLA 2002
  - LEGAL_COURT: Supreme Court of India, High Court of Allahabad
  - LEGAL_CITATION: AIR 2020 SC 123, (2021) 4 SCC 302
  - Standard Entities: PERSON (Accused, Judges), ORG (ED, CBI), MONEY (₹50,000/-)

We built an interactive NER Visualizer into our Streamlit GUI, allowing users to select any of the 25 judgments and dynamically filter entities with color-coded highlights."

--------------------------------------------------------------------------------
SLIDE 18: Statistical N-Grams & BPE Subword Tokenization
--------------------------------------------------------------------------------
[Lavanya Speaks]:
"Finally, I analyzed multi-word legal collocations using statistical N-Grams and trained a Byte Pair Encoding (BPE) subword tokenizer.

N-Gram Analysis:
Indian judicial text is heavily formulaic. In our corpus, we observed:
  - Bigrams: 'high court' (1,842), 'learned counsel' (1,650), 'anticipatory bail' (432)
  - Trigrams: 'learned counsel for' (1,210), 'code of criminal' (480)
  - 4-Grams: 'code of criminal procedure' (245)
  - 5-Grams: 'under section of criminal procedure' (112)

BPE Subwords (6,000 Vocabulary):
To prevent out-of-vocabulary errors on complex legal prefixes and suffixes, BPE splits rare words into known subwords:
  - 'unconstitutional' -> 'un' + 'constitution' + 'al'
  - 'non-bailable' -> 'non' + '-' + 'bail' + 'able'
  - 'misappropriation' -> 'mis' + 'appropria' + 'tion'

I now hand over to Raju to present Pipeline B integration, dual-level indexing, and our evaluation."

================================================================================
SECTION 4: PIPELINE B, EVALUATION & LIVE DEMO (Raju Speaks — Slides 19 to 24)
================================================================================

--------------------------------------------------------------------------------
SLIDE 19: Contextual POS-Aware Lemmatization: 3 Collision Resolutions
--------------------------------------------------------------------------------
[Raju Speaks]:
"Thank you Lavanya. I am Raju. I engineered Pipeline B, constructed the dual-level index, implemented the multi-mode IR engine, conducted the 15-query evaluation, and will walk through our live GUI demo.

First, look at how Contextual POS-Aware Lemmatization eliminates the stemming collisions that Shreerenu exposed. We have three concrete examples:

Case 1: 'execution' vs. 'executive'
  - Pipeline A (Porter): Truncates both to 'execut'. Query 'executive' retrieves 13 judgments with 8 decree false positives. Precision: 38.5%!
  - Pipeline B (POS Lemma): 'execution' [NN] -> lemma 'execution'; 'executive' [JJ/NN] -> lemma 'executive'.
  - Result in B: Query 'executive' retrieves exactly the 5 true magistrate cases (D09, D14, D18, D20, D23). Zero false positives. Precision: 100.0% 🏆!

Case 2: 'suit' vs. 'suitable'
  - Pipeline A (Porter): Truncates both to 'suit'. Query 'suit' retrieves 17 judgments with 7 employment false positives. Precision: 58.8%!
  - Pipeline B (POS Lemma): 'suit' [NN] -> lemma 'suit'; 'suitable' [JJ] -> lemma 'suitable'.
  - Result in B: Query 'suit' retrieves only authentic civil partition/money suits. Zero noise. Precision: 100.0% 🏆!

Case 3: 'learned' vs. 'learning'
  - Pipeline A (Porter): Strips 'learned' to 'learn', destroying the judicial honorific.
  - Pipeline B (POS Lemma): 'learned' [JJ] -> lemma 'learned'; 'learning' [VBG] -> lemma 'learn'.
  - Result in B: Judicial honorifics preserved with 100% precision!

Linguistic Rationale: WordNet and spaCy lemmatizers consult grammatical dictionary lemmas conditioned on part-of-speech context, ensuring legal terms retain their unique semantic identity."

--------------------------------------------------------------------------------
SLIDE 20: Dual-Level Atomic Positional Indexing
--------------------------------------------------------------------------------
[Raju Speaks]:
"In Module 3, I architected Pipeline B's Dual-Level Atomic Positional Index. Instead of indexing only individual single words, our index operates across two synchronized layers:

Layer 1: Atomic Compound Postings
  - Indexes intact multi-word legal phrases and citations as single compound keys:
    'section 302 ipc': {'D11': [14, 82], 'D12': [5], 'D18': [23, 91]}
  - Searching for a compound citation bypasses multi-word coordinate joins completely. It is a direct O(1) hash table lookup!

Layer 2: Constituent Lemma Postings
  - Retains individual lemmatized tokens with sentence and word coordinates for flexible multi-keyword queries.

Index Metrics:
  - Total Indexed Terms: 9,005 terms (+650 compound legal entities over Pipeline A).
  - Query Latency: 0.04 ms (vs. 0.14 ms in Pipeline A).
  - Execution Speedup: 3.5× Faster!"

--------------------------------------------------------------------------------
SLIDE 21: Pipeline B: Legal-Domain-Optimized Architecture (Best Model 🏆)
--------------------------------------------------------------------------------
[Raju Speaks]:
"Here is the complete architectural flowchart of Pipeline B that I assembled.

The sequential flow integrates:
  1. Domain-Aware Normalization (De-hyphenation, acronym shielding)
  2. Custom Legal Regex Tokenizer (Atomic citations)
  3. Protected Legal Stopword Whitelist (49.9% compression)
  4. Contextual POS-Aware Lemmatization
  5. Dual-Level Atomic Positional Indexing (9,005 terms)
  6. Multi-Mode Information Retrieval Engine

Notice our three optimization badges:
  - Atomic Citations Retained: 'Section 302 IPC' and '₹50,000/-' stored as intact single keys.
  - Zero Semantic Collisions: 'execution' and 'executive' kept distinct, reaching 100% precision.
  - Sub-Millisecond Speed: Direct O(1) compound lookup runs in 0.04 ms (3.5× faster than Pipeline A)."

--------------------------------------------------------------------------------
SLIDE 22: Dual-Level Index vs. Conventional Merge: Concrete Query Walkthrough
--------------------------------------------------------------------------------
[Raju Speaks]:
"Let us look at how the Dual-Level Index works in practice compared to conventional coordinate merging, using the query 'Section 302 IPC':

In Pipeline A (Positional Coordinate Merge):
  1. The engine fetches Postings('section'): 1,420 positions across 22 documents.
  2. The engine fetches Postings('302'): 412 positions across 8 documents.
  3. The engine fetches Postings('ipc'): 890 positions across 19 documents.
  4. Iterative Adjacency Check: The algorithm checks if pos(302) = pos(section) + 1 and pos(ipc) = pos(302) + 1.
  - Complexity: O(P1 + P2 + P3) operations. Latency: 0.14 ms.

In Pipeline B (Direct Atomic Hash Lookup):
  1. The query 'Section 302 IPC' is recognized as an atomic compound token by our tokenizer.
  2. Direct Dictionary Lookup: index['section 302 ipc'].
  3. The postings list is returned instantly: {'D11': [14, 82], 'D12': [5], 'D18': [23, 91]}.
  - Zero coordinate joins needed! Complexity: O(1) hash access. Latency: 0.04 ms (3.5× faster! ⚡).

Multi-Mode Capabilities:
  - Boolean Shunting-Yard Parser: '"anticipatory bail" AND NOT murder' evaluates as Postings(anticipatory bail) minus Postings(murder), retrieving D07, D09, D14.
  - Vector Space TF-IDF Cosine Retrieval: Calculates sublinear TF-IDF length-normalized cosine scores for ranked keyword queries like 'cyber fraud bank account'."

--------------------------------------------------------------------------------
SLIDE 23: Controlled Evaluation Across 15 Benchmark Queries
--------------------------------------------------------------------------------
[Raju Speaks]:
"Here is the empirical proof of our system across 15 benchmark legal queries, spanning homicide, narcotics, cybercrime, and economic offenses.

Notice the side-by-side layout: on the left, our empirical comparison table; on the right, the high-resolution comparison chart:
  - Mean Precision: Pipeline A achieved 0.7089. Pipeline B achieved 0.7721 (+8.9% Precision Boost 🏆).
  - Mean Recall: Both pipelines achieved 0.8904 (100% Recall Retained).
  - Mean F1-Score: Pipeline A achieved 0.7549. Pipeline B achieved 0.7979 (+5.7% Harmonic Gain 🏆).
  - Precision@5: Pipeline A achieved 0.7444. Pipeline B achieved 0.8111 (+9.0% Density Improvement 🏆).
  - Query Latency: Pipeline A took 0.14 ms. Pipeline B took 0.04 ms (3.5× Faster Execution 🏆).

Key Finding: Pipeline B improves precision without sacrificing recall. By eliminating false positive collisions while retaining all true documents, Pipeline B decisively wins across every metric!"

--------------------------------------------------------------------------------
SLIDE 24: Interactive Streamlit GUI & Live Evaluation Telemetry
--------------------------------------------------------------------------------
[Raju Speaks]:
"We implemented our system as a full-featured 17-page Streamlit web application with a professional dark navy theme.

Key Architectural Modules:
  - Corpus Analysis: Dashboard Overview, Document Explorer, Corpus Statistics.
  - NLP Workbench: Tokenizer Workbench, Stopword Policy, Stem/Lemma Table, Custom POS & ML Classifier, Legal NER Visualizer, N-Grams, BPE Subwords.
  - Retrieval Engine: Flagship Search, Positional Index Explorer, Boolean Builder, Pipeline A vs B Comparison, and Retrieval Evaluation.

Live Telemetry Feature:
Whenever a user searches ANY query—such as 'smuggl' or 'bail'—our application computes live Precision, Recall, and F1-score metric cards dynamically on the screen, accompanied by an academic monospace Forensic IR Execution Trace showing the postings verification, TP, FP, and FN classifications.

I will now open http://localhost:8501 for our live demonstration."

================================================================================
LIVE STREAMLIT GUI DEMONSTRATION SCRIPT (Raju Presents Live)
================================================================================
[Raju switches browser to http://localhost:8501]:
1. Step 1: Corpus Explorer
   "Ma'am, here is our Document Explorer. We can inspect all 25 Supreme Court and High Court judgments, view metadata, and examine sentence and token counts."

2. Step 2: NLP Analysis & Stemming Collision
   "Navigating to 'Stemming vs Lemmatization': Notice our side-by-side comparison table. When we enter 'execution' and 'executive', Pipeline A collapses both to 'execut', whereas Pipeline B cleanly preserves 'execution' and 'executive' as distinct dictionary lemmas."

3. Step 3: Flagship Retrieval & Collision Demonstration
   "Now in 'Pipeline A vs B Comparison': Let us enter the query 'executive'.
    - Pipeline A retrieves 13 judgments with 8 false positives (decree executions), resulting in 38.5% precision.
    - Pipeline B retrieves only 5 judgments (all true executive magistrate cases), achieving 100% precision!
    Notice the live IR metric cards and forensic execution trace rendered right above the judgments."

4. Step 4: Boolean Search
   "In 'Boolean Query Builder': We enter 'bail AND murder NOT anticipatory'. Our Shunting-Yard parser evaluates the expression through set operations in sub-milliseconds."

5. Step 5: Benchmark Evaluation
   "Finally, in 'Retrieval Evaluation': The system runs the automated 15-query benchmark, generating the comparison bar chart confirming Pipeline B's superior 0.7721 precision and 0.7979 F1-score."

================================================================================
SECTION 5: SYNTHESIS & VIVA DEFENSE (All Members — Slide 25)
================================================================================

--------------------------------------------------------------------------------
SLIDE 25: Conclusion & Final Defense Verdict
--------------------------------------------------------------------------------
[All Members Join]:
"In conclusion, our project proves that legal NLP requires domain preservation. Generic NLP fails on Indian case law because citations fragment, liability inverts, and stems collide.

Summary of Contributions:
  - Brunda: Ingested 25 judgments (257k tokens), engineered conservative cleaning, and evaluated stemmers (Porter vs Snowball vs Lancaster).
  - Shreerenu: Formulated the 8-term Protected Stopword Policy, architected baseline Pipeline A, and proved the over-stemming collision bottlenecks.
  - Lavanya: Engineered the Custom Legal Regex Tokenizer, built the Supervised ML POS Classifier (76.7% accuracy), and implemented Legal NER.
  - Raju: Engineered contextual lemmatization, built the Dual-Level Atomic Positional Index, constructed the multi-mode IR engine, and proved Pipeline B's empirical superiority (+8.9% precision, 3.5× faster).

Pipeline B stands conclusively established as the Best Performing Retrieval Pipeline.

Thank you Ma'am and esteemed faculty. We welcome your questions!"

================================================================================
END OF SCRIPT
================================================================================
