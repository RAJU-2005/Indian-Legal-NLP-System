import re

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Domain-Specific Text Analysis & Retrieval System for Indian Legal Judgments — Presentation</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-color: #0A0E1A;
            --card-bg: #111827;
            --card-border: #1E293B;
            --accent-blue: #3B82F6;
            --accent-gold: #D97706;
            --accent-green: #10B981;
            --accent-red: #EF4444;
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
            display: flex;
            flex-direction: column;
        }

        /* Top Progress Bar */
        .progress-bar-container {
            width: 100%;
            height: 4px;
            background: #1E293B;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 100;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #3B82F6, #10B981);
            width: 4%;
            transition: width 0.3s ease;
        }

        /* Header Navigation Info */
        .pres-header {
            padding: 10px 28px;
            background: rgba(17, 24, 39, 0.95);
            border-bottom: 1px solid var(--card-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.84rem;
            color: var(--text-secondary);
            z-index: 10;
        }
        .speaker-badge {
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.4);
            color: #60A5FA;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.78rem;
        }

        /* Deck & Slides */
        .deck-container {
            flex: 1;
            position: relative;
            overflow: hidden;
            width: 100%;
        }

        .slide {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: calc(100vh - 96px);
            max-height: calc(100vh - 96px);
            padding: 16px 48px;
            box-sizing: border-box;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.25s ease, transform 0.25s ease;
            transform: translateY(8px);
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .slide.active {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        /* Slide Typography */
        .slide-tag {
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-gold);
            margin-bottom: 4px;
        }
        .slide-title {
            font-size: 1.75rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 6px;
            line-height: 1.25;
        }
        .slide-subtitle {
            font-size: 0.92rem;
            color: var(--text-secondary);
            margin-bottom: 16px;
            line-height: 1.45;
        }

        /* Content Layouts */
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            align-items: start;
        }
        .grid-3 {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 16px;
        }
        .grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
        }

        /* Cards */
        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }
        .card-blue { border-left: 4px solid var(--accent-blue); }
        .card-green { border-left: 4px solid var(--accent-green); }
        .card-gold { border-left: 4px solid var(--accent-gold); }
        .card-red { border-left: 4px solid var(--accent-red); }

        .card-title {
            font-size: 1.0rem;
            font-weight: 700;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .card-body {
            font-size: 0.85rem;
            color: #CBD5E1;
            line-height: 1.55;
        }
        .card-body b {
            color: #F8FAFC;
        }
        .card-body code {
            background: #0B0F19;
            color: #FBBF24;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', Consolas, monospace;
            font-size: 0.82rem;
        }

        /* Highlight Boxes */
        .callout-box {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 10px 16px;
            margin: 8px 0;
            font-size: 0.84rem;
            line-height: 1.45;
        }
        .callout-danger {
            border-left: 4px solid var(--accent-red);
            background: rgba(239, 68, 68, 0.08);
        }
        .callout-success {
            border-left: 4px solid var(--accent-green);
            background: rgba(16, 185, 129, 0.08);
        }

        /* Metric KPI Badges */
        .kpi-container {
            display: flex;
            gap: 12px;
            margin-top: 10px;
        }
        .kpi-badge {
            background: #0B0F19;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 8px 14px;
            flex: 1;
            text-align: center;
        }
        .kpi-val {
            font-size: 1.25rem;
            font-weight: 800;
            color: #60A5FA;
        }
        .kpi-label {
            font-size: 0.7rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-weight: 600;
            margin-top: 2px;
        }

        /* Tables */
        table.pres-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
            margin-top: 8px;
        }
        table.pres-table th, table.pres-table td {
            border: 1px solid var(--card-border);
            padding: 7px 12px;
            text-align: left;
        }
        table.pres-table th {
            background: #1E293B;
            color: #94A3B8;
            font-weight: 700;
        }
        table.pres-table tr:nth-child(even) {
            background: rgba(30, 41, 59, 0.35);
        }

        /* Flowchart Pipeline CSS */
        .flowchart-wrapper {
            display: flex;
            flex-direction: column;
            gap: 12px;
            width: 100%;
            margin-top: 6px;
        }
        .flowchart-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            width: 100%;
        }
        .flowchart-node {
            background: #111827;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 12px 10px;
            flex: 1;
            min-height: 90px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        .flowchart-node.node-blue { border-color: #3B82F6; background: rgba(59, 130, 246, 0.08); }
        .flowchart-node.node-gold { border-color: #D97706; background: rgba(217, 119, 6, 0.08); }
        .flowchart-node.node-green { border-color: #10B981; background: rgba(16, 185, 129, 0.08); }
        .flowchart-node.node-red { border-color: #EF4444; background: rgba(239, 68, 68, 0.08); }

        .flowchart-node-title {
            font-size: 0.85rem;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 4px;
        }
        .flowchart-node-desc {
            font-size: 0.74rem;
            color: #94A3B8;
            line-height: 1.3;
        }
        .flowchart-arrow {
            color: #64748B;
            font-size: 1.1rem;
            font-weight: 800;
            padding: 0 2px;
        }
        .flowchart-callouts {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin-top: 6px;
        }

        /* Image Display */
        .slide-img-container {
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 8px;
            overflow: hidden;
            background: transparent;
        }
        .slide-img-container img {
            max-width: 100%;
            max-height: 340px;
            width: auto;
            object-fit: contain;
            border-radius: 8px;
        }

        /* Bottom Controls */
        .pres-footer {
            height: 48px;
            padding: 0 28px;
            background: #111827;
            border-top: 1px solid var(--card-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.84rem;
            z-index: 10;
        }
        .controls-group {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .btn-nav {
            background: #1E293B;
            color: #F8FAFC;
            border: 1px solid #334155;
            padding: 5px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.82rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
        }
        .btn-nav:hover {
            background: var(--accent-blue);
            border-color: var(--accent-blue);
        }
        .slide-counter {
            font-weight: 700;
            color: #F8FAFC;
            min-width: 90px;
            text-align: center;
        }

        /* Title Slide Custom */
        .title-hero {
            text-align: center;
            max-width: 900px;
            margin: 0 auto;
        }
        .title-hero h1 {
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #FFFFFF 0%, #93C5FD 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .title-hero .dept {
            font-size: 0.98rem;
            color: #94A3B8;
            margin-bottom: 20px;
        }
        .team-box {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-top: 24px;
        }
        .member-card {
            background: #111827;
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 14px 12px;
            text-align: center;
        }
        .member-name {
            font-weight: 700;
            font-size: 0.98rem;
            color: #FFFFFF;
        }
        .member-role {
            font-size: 0.72rem;
            color: #60A5FA;
            margin-top: 4px;
            font-weight: 600;
            line-height: 1.35;
        }

        /* Presenter Notes Overlay */
        .notes-panel {
            display: none;
            position: fixed;
            bottom: 54px;
            right: 28px;
            width: 440px;
            max-height: 260px;
            background: rgba(15, 23, 42, 0.96);
            border: 1px solid var(--accent-gold);
            border-radius: 10px;
            padding: 16px;
            font-size: 0.82rem;
            line-height: 1.5;
            color: #E2E8F0;
            overflow-y: auto;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            z-index: 100;
        }
        .notes-panel.active { display: block; }
        .notes-header {
            font-weight: 700;
            color: #FBBF24;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
        }
    </style>
</head>
<body>

    <!-- Top Progress Bar -->
    <div class="progress-bar-container">
        <div class="progress-bar" id="progressBar"></div>
    </div>

    <!-- Header Navigation Info -->
    <div class="pres-header">
        <div>
            <span><b>Vidyashilp University</b> · School of Advanced Computing · NLP Assessment 1</span>
        </div>
        <div id="speakerBadge" class="speaker-badge">
            👤 All Members Overview
        </div>
    </div>

    <!-- Slide Deck Container -->
    <div class="deck-container">

        <!-- SLIDE 1: Title & Team Overview -->
        <div class="slide active" data-speaker="Team Introduction" data-notes="Good morning Ma'am and faculty. Today our team is presenting our NLP Assessment 1 project: Domain-Specific Text Analysis and Retrieval System for Indian Legal Judgments. Our team consists of four members: Brunda covers raw ingestion, conservative cleaning, and stemmer evaluation; Shreerenu handles stopword polarity, Pipeline A architecture, and positional inverted indexing; Lavanya develops the domain NLP innovations including Custom Legal Regex, ML POS classification, and Legal NER; and Raju engineers Pipeline B, dual-level indexing, the multi-mode IR engine, and our empirical evaluation.">
            <div class="title-hero">
                <div class="slide-tag">Natural Language Processing · Seventh Semester</div>
                <h1>Domain-Specific Text Analysis & Retrieval System for Indian Legal Judgments</h1>
                <div class="dept">Comparative Engineering Study of Conventional Baseline (Pipeline A) vs. Legal-Domain-Optimized (Pipeline B)</div>
                <div style="display:flex; justify-content:center; gap:10px;">
                    <span style="background:rgba(59,130,246,0.15); color:#60A5FA; border:1px solid rgba(59,130,246,0.35); padding:4px 12px; border-radius:9999px; font-size:0.78rem; font-weight:600;">📜 25 Verified Judgments (D01–D25)</span>
                    <span style="background:rgba(16,185,129,0.15); color:#34D399; border:1px solid rgba(16,185,129,0.35); padding:4px 12px; border-radius:9999px; font-size:0.78rem; font-weight:600;">🏆 Best Model: Pipeline B</span>
                    <span style="background:rgba(217,119,6,0.15); color:#FBBF24; border:1px solid rgba(217,119,6,0.35); padding:4px 12px; border-radius:9999px; font-size:0.78rem; font-weight:600;">⚡ 15 Benchmark Legal Queries</span>
                </div>

                <div class="team-box">
                    <div class="member-card">
                        <div class="member-name">👤 Brunda</div>
                        <div class="member-role">Data Ingestion, Text Cleaning & Baseline Tokenization/Stemming</div>
                    </div>
                    <div class="member-card">
                        <div class="member-name">👤 Shreerenu</div>
                        <div class="member-role">Stopwords, Pipeline A Architecture & Word Inverted Index</div>
                    </div>
                    <div class="member-card">
                        <div class="member-name">👤 Lavanya</div>
                        <div class="member-role">Custom Legal Tokenizer, ML POS Tagger & Legal NER</div>
                    </div>
                    <div class="member-card">
                        <div class="member-name">👤 Raju</div>
                        <div class="member-role">Contextual Lemmatization, Dual Index, IR Engine & Live Evaluation</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 2: Problem Statement & Why Legal NLP Fails -->
        <div class="slide" data-speaker="Brunda: Foundations & Ingestion" data-notes="I will begin by explaining why general off-the-shelf NLP fails on Indian case law. Legal texts are not regular prose. Punctuation carries statutory meaning, section numbers combine numbers and sub-clauses, and removing functional words reverses criminal guilt. Here we show three concrete examples for each of the three major NLP failure modes.">
            <div class="slide-tag">Problem Formulation · Indian Legal Jurisprudence</div>
            <div class="slide-title">Why Generic Off-the-Shelf NLP Fails on Indian Case Law</div>
            <div class="slide-subtitle">Statutory reasoning, compound citations, and criminal polarity demand domain-specialized text processing.</div>
            
            <div class="grid-3">
                <div class="card card-red">
                    <div class="card-title" style="color:#F87171;"><i class="fa-solid fa-scissors"></i> Citation Fragmentation</div>
                    <div class="card-body">
                        Standard tokenizers split provisions at punctuation:<br/><br/>
                        • <b>Ex 1:</b> <code>Section 302 IPC</code> &rarr; <code>['Section', '302', 'IPC']</code><br/>
                        *(Splits penal section into 3 unrelated words)*<br/>
                        • <b>Ex 2:</b> <code>Article 21 of Constitution</code> &rarr; <code>['Article', '21', 'of', 'Constitution']</code><br/>
                        *(Shatters fundamental right entity)*<br/>
                        • <b>Ex 3:</b> <code>₹50,000/- bail bond</code> &rarr; <code>['₹', '50', ',', '000', '/', '-']</code><br/>
                        *(Fragments monetary threshold into 6 tokens)*
                    </div>
                </div>
                <div class="card card-red">
                    <div class="card-title" style="color:#F87171;"><i class="fa-solid fa-triangle-exclamation"></i> Semantic Liability Inversion</div>
                    <div class="card-body">
                        Standard stopword filters discard negation words:<br/><br/>
                        • <b>Ex 1:</b> <i>"applicant is <b>not</b> guilty"</i> &rarr; <code>['applicant', 'guilty']</code><br/>
                        *(Inverts complete innocence to guilt!)*<br/>
                        • <b>Ex 2:</b> <i>"<b>without</b> reasonable doubt"</i> &rarr; <code>['reasonable', 'doubt']</code><br/>
                        *(Inverts prosecution burden of proof!)*<br/>
                        • <b>Ex 3:</b> <i>"<b>no</b> grounds for detention"</i> &rarr; <code>['grounds', 'detention']</code><br/>
                        *(Turns release order into detention justification!)*
                    </div>
                </div>
                <div class="card card-red">
                    <div class="card-title" style="color:#F87171;"><i class="fa-solid fa-burst"></i> Over-Stemming Collisions</div>
                    <div class="card-body">
                        Algorithmic stemmers (Porter) truncate endings blindly:<br/><br/>
                        • <b>Ex 1:</b> <code>execution</code> vs. <code>executive</code> &rarr; <code>execut</code><br/>
                        *(Decree execution conflated with Magistrate!)*<br/>
                        • <b>Ex 2:</b> <code>suit</code> (lawsuit) vs. <code>suitable</code> &rarr; <code>suit</code><br/>
                        *(Civil lawsuit mixed with employment adjectives)*<br/>
                        • <b>Ex 3:</b> <code>custody</code> vs. <code>custodian</code> &rarr; Lancaster <code>cust</code><br/>
                        *(Remand custody conflated with property trustee)*
                    </div>
                </div>
            </div>
            <div class="callout-box callout-success" style="margin-top:14px;">
                <b>The Assignment Framework:</b> Select &rarr; Order &rarr; Implement &rarr; Compare &rarr; Evaluate &rarr; Justify.
            </div>
        </div>

        <!-- SLIDE 3: Corpus Ingestion & Domain-Aware Normalization -->
        <div class="slide" data-speaker="Brunda: Foundations & Ingestion" data-notes="Here is our dataset and normalization strategy. We ingested 25 verified PDF judgments from the Supreme Court and High Courts, spanning 257k tokens and 6 legal sectors. Crucially, to keep normalization domain-aware, we designed four specific techniques: statutory case-folding, OCR line-break repair, quote preservation, and penal clause protection.">
            <div class="slide-tag">Module 1 · Dataset Ingestion & Normalization</div>
            <div class="slide-title">Corpus Architecture & Domain-Aware Normalization</div>
            <div class="slide-subtitle">Extracted 25 full-text Indian Supreme Court & High Court judgments spanning 6 core legal sectors.</div>

            <div class="grid-2">
                <div class="card card-blue">
                    <div class="card-title" style="color:#60A5FA;"><i class="fa-solid fa-scale-balanced"></i> Verified Legal Sectors & Telemetry</div>
                    <div class="card-body">
                        • <b>Cybercrime & IT Act:</b> D01–D05 (IT Act 66-D, online fraud, cheating)<br/>
                        • <b>Economic Offenses / PMLA:</b> D06–D08 (ED prosecution, gold diversion)<br/>
                        • <b>Narcotics (NDPS Act):</b> D09–D10 (Commercial quantity contraband)<br/>
                        • <b>Violent Crimes (IPC 302):</b> D11–D13 (Homicide, bail appeals)<br/>
                        • <b>Matrimonial / Dowry:</b> D14–D15 (IPC 498A/304B death)<br/>
                        • <b>Preventive Detention:</b> D21–D22 (Article 226 Habeas Corpus)<br/>
                        <div class="kpi-container" style="margin-top:10px;">
                            <div class="kpi-badge"><div class="kpi-val">25</div><div class="kpi-label">Judgments</div></div>
                            <div class="kpi-badge"><div class="kpi-val">257,849</div><div class="kpi-label">Tokens</div></div>
                            <div class="kpi-badge"><div class="kpi-val">8,552</div><div class="kpi-label">Sentences</div></div>
                            <div class="kpi-badge"><div class="kpi-val">10,819</div><div class="kpi-label">Vocabulary</div></div>
                        </div>
                    </div>
                </div>
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-shield-halved"></i> 4 Domain-Aware Normalization Techniques</div>
                    <div class="card-body">
                        1. <b>Statutory Case-Folding:</b> Lowercases running text while shielding statutory uppercase acronyms (<code>IPC</code>, <code>CrPC</code>, <code>AIR</code>, <code>SCC</code>, <code>NDPS</code>) so legal authority is not degraded.<br/><br/>
                        2. <b>Line-Break De-Hyphenation:</b> Repairs PDF/OCR broken words across line wraps (e.g. <code>crimi-\nnal</code> &rarr; <code>criminal</code>, <code>prose-\ncution</code> &rarr; <code>prosecution</code>).<br/><br/>
                        3. <b>Quotation & Latin Maxim Retention:</b> Preserves quotation marks (<code>"..."</code>) and Latin doctrines (<code>mens rea</code>, <code>suo motu</code>, <code>ultra vires</code>) for exact phrase queries.<br/><br/>
                        4. <b>Sub-Clause Punctuation Protection:</b> Retains parentheses in statutory subsections (<code>Section 376(2)(i)</code>) and currency symbols (<code>₹50,000/-</code>).
                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 4: Text Cleaning: Conservative vs Aggressive -->
        <div class="slide" data-speaker="Brunda: Foundations & Ingestion" data-notes="I designed the text cleaning stage. Aggressive cleaning strips all non-alphanumerics, which is disastrous in law because it destroys section sub-clauses and currency symbols. Conservative cleaning standardizes line-breaks while preserving quotes, clause brackets, and rupee symbols.">
            <div class="slide-tag">Module 1 · Text Normalization</div>
            <div class="slide-title">Conservative vs. Aggressive Text Cleaning</div>
            <div class="slide-subtitle">Preserving statutory sub-clauses, currency markers, and quotation boundaries.</div>

            <div class="grid-2">
                <div class="card card-red">
                    <div class="card-title" style="color:#F87171;"><i class="fa-solid fa-xmark"></i> Aggressive Cleaning (Flawed Baseline)</div>
                    <div class="card-body">
                        • Strips all punctuation and symbols indiscriminately.<br/>
                        • <b>Example 1:</b> <code>₹50,000/-</code> &rarr; <code>50 000</code><br/>
                        *(Currency symbol erased; number split into two meaningless pieces)*<br/><br/>
                        • <b>Example 2:</b> <code>Section 376(2)(i) IPC</code> &rarr; <code>section 376 2 i ipc</code><br/>
                        *(Sub-clause brackets deleted; destroys POCSO child rape threshold)*
                    </div>
                </div>
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-check"></i> Conservative Cleaning (Domain-Aware)</div>
                    <div class="card-body">
                        • Normalizes line-break hyphenations (<code>crimi-\nnal</code> &rarr; <code>criminal</code>).<br/>
                        • Preserves quotation marks (<code>"..."</code>) for exact quoted phrase matching.<br/>
                        • Retains currency symbols (<code>₹</code>) and statutory sub-clause parentheses.<br/>
                        • Retains hyphenated legal constructs (<code>non-bailable</code>, <code>suo-motu</code>).
                    </div>
                </div>
            </div>
            <div class="callout-box callout-success" style="margin-top:14px;">
                <b>Engineering Outcome:</b> Preserved 100% of financial thresholds and penal clause definitions across all 25 PDF extractions.
            </div>
        </div>

        <!-- SLIDE 5: Conventional Tokenization Paradigms (5 Real Examples) -->
        <div class="slide" data-speaker="Brunda: Foundations & Ingestion" data-notes="Next, I benchmarked conventional tokenizers. Whitespace keeps words together but leaves punctuation attached. NLTK word tokenizer uses Penn Treebank rules, which fragments citations. Look at these 5 real examples from our project corpus showing how standard tokenization breaks penal sections, bail bonds, Latin writs, and court citations.">
            <div class="slide-tag">Module 2 · Tokenization Evaluation</div>
            <div class="slide-title">Conventional Tokenization & Citation Splitting: 5 Project Examples</div>
            <div class="slide-subtitle">Empirical evaluation of Whitespace and Standard NLTK Word Tokenizers on our 25-judgment corpus.</div>

            <table class="pres-table">
                <tr>
                    <th>Input Judicial Sentence (Corpus)</th>
                    <th>NLTK Word Tokenizer (Penn Treebank)</th>
                    <th>Linguistic Defect Observed</th>
                </tr>
                <tr>
                    <td><code>Section 302 IPC</code></td>
                    <td><code>['Section', '302', 'IPC']</code></td>
                    <td>Splits statutory unit into 3 pieces; searches match any section</td>
                </tr>
                <tr>
                    <td><code>bail bond of ₹50,000/-</code></td>
                    <td><code>['bail', 'bond', 'of', '₹', '50,000', '/', '-']</code></td>
                    <td>Splits monetary condition into 4 isolated punctuation/digit tokens</td>
                </tr>
                <tr>
                    <td><code>writ of habeas corpus</code></td>
                    <td><code>['writ', 'of', 'habeas', 'corpus']</code></td>
                    <td>Latin maxim split; 'habeas' has zero independent legal meaning</td>
                </tr>
                <tr>
                    <td><code>Section 376(2)(i) IPC</code></td>
                    <td><code>['Section', '376', '(', '2', ')', '(', 'i', ')', 'IPC']</code></td>
                    <td>Destroys parentheses; erases POCSO aggravated rape threshold</td>
                </tr>
                <tr>
                    <td><code>AIR 2020 SC 1450</code></td>
                    <td><code>['AIR', '2020', 'SC', '1450']</code></td>
                    <td>Fragments All India Reporter case citation into arbitrary chunks</td>
                </tr>
            </table>

            <div class="card card-gold" style="margin-top:14px;">
                <div class="card-title" style="color:#FBBF24;"><i class="fa-solid fa-lightbulb"></i> Brunda's Rationale & Key Finding:</div>
                <div class="card-body">
                    Conventional tokenizers treat periods, slashes, and spaces within citations as general word boundaries. This creates a severe dependency problem for downstream indexing: multi-word penal provisions require expensive positional merge operations in Pipeline A!
                </div>
            </div>
        </div>

        <!-- SLIDE 6: Morphological Stemming Experiments (Porter vs Snowball vs Lancaster) -->
        <div class="slide" data-speaker="Brunda: Foundations & Ingestion" data-notes="For stemming in Pipeline A, why did we choose Porter over Lancaster? Lancaster is hyper-aggressive and cuts words destructively: legal becomes leg, custody becomes cust, and bailment becomes bail. But why Porter over Snowball? On our 257k legal tokens, Porter and Snowball produce 98.4% identical stems. More crucially, Snowball still suffers from the exact same semantic collisions: both collapse execution and executive to execut, and suit and suitable to suit! Porter was selected because it is the canonical IR benchmark standard in literature, proving that suffix stripping itself is fundamentally flawed for law. I now hand over to Shreerenu.">
            <div class="slide-tag">Module 2 · Morphological Reduction</div>
            <div class="slide-title">Stemming Experiments: Porter vs. Snowball vs. Lancaster</div>
            <div class="slide-subtitle">Why Porter over Lancaster? And why Porter over Snowball? Empirical justifications on legal text.</div>

            <table class="pres-table">
                <tr>
                    <th>Legal Term</th>
                    <th>Porter Stemmer</th>
                    <th>Snowball Stemmer</th>
                    <th>Lancaster Stemmer</th>
                    <th>Linguistic & Legal Defect Analysis</th>
                </tr>
                <tr>
                    <td><code>legal</code></td>
                    <td><code>legal</code></td>
                    <td><code>legal</code></td>
                    <td><code>leg</code> ⚠️</td>
                    <td>Lancaster destroys root; conflates jurisprudence with human leg!</td>
                </tr>
                <tr>
                    <td><code>custody</code></td>
                    <td><code>custodi</code></td>
                    <td><code>custodi</code></td>
                    <td><code>cust</code> ⚠️</td>
                    <td>Lancaster chops root too short ('cust'), losing identity entirely</td>
                </tr>
                <tr>
                    <td><code>bailment</code></td>
                    <td><code>bailment</code></td>
                    <td><code>bailment</code></td>
                    <td><code>bail</code> ⚠️</td>
                    <td>Lancaster conflates 'bailment' (contract) with criminal 'bail' (surety)!</td>
                </tr>
                <tr>
                    <td><code>appellants</code></td>
                    <td><code>appel</code></td>
                    <td><code>appel</code></td>
                    <td><code>appl</code> ⚠️</td>
                    <td>Lancaster conflates court 'appellant' with 'apple' or 'apply'!</td>
                </tr>
                <tr>
                    <td><code>preliminary</code></td>
                    <td><code>preliminari</code></td>
                    <td><code>preliminari</code></td>
                    <td><code>prelimin</code> ⚠️</td>
                    <td>Lancaster over-truncates statutory procedure terms</td>
                </tr>
                <tr>
                    <td><code>execution</code> vs. <code>executive</code></td>
                    <td><code>execut</code> / <code>execut</code> ⚠️</td>
                    <td><code>execut</code> / <code>execut</code> ⚠️</td>
                    <td><code>execut</code> / <code>execut</code> ⚠️</td>
                    <td><b>Both Porter & Snowball fail!</b> Both collapse decree with magistrate</td>
                </tr>
            </table>

            <div class="callout-box callout-danger" style="margin-top:10px;">
                <b>Why Porter Over Snowball?</b> On our 257k tokens, Porter and Snowball produce <b>98.4% identical roots</b>. Crucially, Snowball fails on the exact same legal collisions. Porter (1980) was selected for Pipeline A as the universal canonical IR baseline standard (Manning et al., 2008), establishing that algorithmic suffix stripping itself is inadequate, directly motivating Contextual POS Lemmatization in Pipeline B!
            </div>
        </div>

        <!-- SLIDE 7: Stopwords & The Negation Inversion Problem -->
        <div class="slide" data-speaker="Shreerenu: Baseline & Pipeline A" data-notes="Thank you Brunda. I am Shreerenu. I investigated stopwords and architected Pipeline A. Look at this slide: in standard NLP, stopwords are stripped to save space. But in criminal law, words like 'not' and 'no' determine whether an accused is innocent or guilty! Removing them inverts criminal liability.">
            <div class="slide-tag">Module 2 · Semantic Polarity</div>
            <div class="slide-title">Stopwords & The Catastrophic Inversion of Liability</div>
            <div class="slide-subtitle">Why standard English stopword lists cannot be blindly applied to criminal jurisprudence.</div>

            <div class="grid-2">
                <div class="card card-red">
                    <div class="card-title" style="color:#F87171;"><i class="fa-solid fa-ban"></i> Standard NLTK Stopword List (179 Words)</div>
                    <div class="card-body">
                        Purges functional grammar tokens unconditionally:<br/>
                        <code>not</code>, <code>no</code>, <code>nor</code>, <code>without</code>, <code>unless</code>, <code>except</code>, <code>until</code>, <code>against</code><br/><br/>
                        <b>Catastrophic Inversion in Case Law:</b><br/>
                        • <i>"applicant is <b>not guilty</b>"</i> &rarr; <code>['applicant', 'guilty']</code><br/>
                        • <i>"order passed <b>without jurisdiction</b>"</i> &rarr; <code>['order', 'passed', 'jurisdiction']</code><br/>
                        • <i>"<b>no offence</b> made out"</i> &rarr; <code>['offence', 'made']</code>
                    </div>
                </div>
                <div class="card card-blue">
                    <div class="card-title" style="color:#60A5FA;"><i class="fa-solid fa-shield-halved"></i> Impact on Information Retrieval</div>
                    <div class="card-body">
                        If a lawyer searches for judgments where an accused was <b>"not guilty"</b> under PMLA:<br/><br/>
                        • With standard stopword removal, the query becomes <code>['guilty']</code>.<br/>
                        • The search engine retrieves all judgments where the accused was found <b>guilty</b>!<br/>
                        • <b>Precision collapses to 0%</b> for all negative condition queries!
                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 8: The Protected Legal Stopword Policy -->
        <div class="slide" data-speaker="Shreerenu: Baseline & Pipeline A" data-notes="To solve this, I formulated our Protected Legal Stopword Policy. We whitelist 8 critical polarity and condition terms. We still remove general fluff like 'the', 'is', 'at', reducing the corpus by 49.9%, but we protect the statutory truth.">
            <div class="slide-tag">Module 2 · Stopword Engineering</div>
            <div class="slide-title">The Protected Legal Stopword Policy</div>
            <div class="slide-subtitle">Formulating an authoritative polarity whitelist while maintaining corpus reduction.</div>

            <div class="card card-green">
                <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-shield-virus"></i> The 8 Protected Polarity & Condition Operators:</div>
                <div class="card-body" style="font-size:1.05rem; text-align:center; padding:8px 0;">
                    <code>not</code> &nbsp;·&nbsp; <code>no</code> &nbsp;·&nbsp; <code>never</code> &nbsp;·&nbsp; <code>without</code> &nbsp;·&nbsp; <code>unless</code> &nbsp;·&nbsp; <code>except</code> &nbsp;·&nbsp; <code>until</code> &nbsp;·&nbsp; <code>against</code>
                </div>
            </div>

            <div class="grid-3" style="margin-top:14px;">
                <div class="kpi-badge">
                    <div class="kpi-val">257,849</div>
                    <div class="kpi-label">Raw Corpus Tokens</div>
                </div>
                <div class="kpi-badge">
                    <div class="kpi-val">129,181</div>
                    <div class="kpi-label">Pipeline A Post-Stopwords</div>
                </div>
                <div class="kpi-badge">
                    <div class="kpi-val" style="color:#10B981;">49.9% Reduction</div>
                    <div class="kpi-label">Corpus Compression Achieved</div>
                </div>
            </div>
            <div class="callout-box callout-success" style="margin-top:12px;">
                <b>Design Decision:</b> Both Pipeline A and Pipeline B incorporate this protected negation policy so that the comparative evaluation reflects morphological and tokenization differences, rather than simple polarity errors.
            </div>
        </div>

        <!-- SLIDE 9: Pipeline A Architecture Diagram (Clean Vector Flowchart) -->
        <div class="slide" data-speaker="Shreerenu: Baseline & Pipeline A" data-notes="Here is the complete architecture of Pipeline A that I orchestrated. Raw PDF goes through conservative cleaning, standard NLTK word tokenization, protected stopwords, Porter stemming, and into a word-level positional inverted index. Notice our clean architecture layout with exactly one red callout under Morphological Stemming showing where Porter collides.">
            <div class="slide-tag">Module 3 · Baseline Architecture</div>
            <div class="slide-title">Pipeline A: Conventional Baseline Architecture</div>
            <div class="slide-subtitle">Sequential data-flow of the conventional baseline pipeline with single embedded failure callouts.</div>

            <div class="flowchart-wrapper">
                <div class="flowchart-row">
                    <div class="flowchart-node node-blue">
                        <div class="flowchart-node-title"><i class="fa-solid fa-file-pdf"></i> Raw Judgments</div>
                        <div class="flowchart-node-desc">25 Court PDFs<br/>(257,849 tokens)</div>
                    </div>
                    <div class="flowchart-arrow">&rarr;</div>
                    <div class="flowchart-node node-blue">
                        <div class="flowchart-node-title"><i class="fa-solid fa-broom"></i> Conservative Cleaning</div>
                        <div class="flowchart-node-desc">Hyphen repair,<br/>quotes & ₹ preserved</div>
                    </div>
                    <div class="flowchart-arrow">&rarr;</div>
                    <div class="flowchart-node node-red">
                        <div class="flowchart-node-title"><i class="fa-solid fa-scissors"></i> Conventional Tokenizer</div>
                        <div class="flowchart-node-desc">Standard NLTK<br/>Penn Treebank rules</div>
                    </div>
                    <div class="flowchart-arrow">&rarr;</div>
                    <div class="flowchart-node node-gold">
                        <div class="flowchart-node-title"><i class="fa-solid fa-filter"></i> Stopword Removal</div>
                        <div class="flowchart-node-desc">NLTK 179 + Protected<br/>Negation Policy</div>
                    </div>
                    <div class="flowchart-arrow">&rarr;</div>
                    <div class="flowchart-node node-red">
                        <div class="flowchart-node-title"><i class="fa-solid fa-burst"></i> Porter Stemmer</div>
                        <div class="flowchart-node-desc">Algorithmic rule-based<br/>suffix stripping</div>
                    </div>
                    <div class="flowchart-arrow">&rarr;</div>
                    <div class="flowchart-node node-blue">
                        <div class="flowchart-node-title"><i class="fa-solid fa-database"></i> Positional Index</div>
                        <div class="flowchart-node-desc">Word-level postings<br/>(8,355 unique stems)</div>
                    </div>
                    <div class="flowchart-arrow">&rarr;</div>
                    <div class="flowchart-node node-blue">
                        <div class="flowchart-node-title"><i class="fa-solid fa-magnifying-glass"></i> Retrieval Engine</div>
                        <div class="flowchart-node-desc">Positional Merge<br/>Mean F1: 0.7549</div>
                    </div>
                </div>

                <div class="flowchart-callouts">
                    <div class="callout-box callout-danger" style="margin:0;">
                        <b>⚠️ Citation Fragmentation:</b> <code>Section 302 IPC</code> is split into <code>['Section', '302', 'IPC']</code>, losing compound identity.
                    </div>
                    <div class="callout-box callout-danger" style="margin:0;">
                        <b>⚠️ Over-Stemming Collision:</b> <code>execution</code> & <code>executive</code> &rarr; <code>execut</code> (Causes 8 false positives; 38.5% precision).
                    </div>
                    <div class="callout-box callout-danger" style="margin:0;">
                        <b>⚠️ Coordinate Join Overhead:</b> Quoted phrases require iterative $O(N+M)$ positional merges (0.14 ms query latency).
                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 10: Word-Level Positional Indexing -->
        <div class="slide" data-speaker="Shreerenu: Baseline & Pipeline A" data-notes="I implemented the positional inverted index for Pipeline A. It stores terms mapped to document IDs, sentence IDs, and word offsets. It indexes 8,355 unique stemmed terms across all 25 judgments.">
            <div class="slide-tag">Module 3 · Inverted Index Architecture</div>
            <div class="slide-title">Pipeline A: Word-Level Positional Inverted Index</div>
            <div class="slide-subtitle">Coordinate tracking across document, sentence, and word offsets.</div>

            <div class="grid-2">
                <div class="card card-blue">
                    <div class="card-title" style="color:#60A5FA;"><i class="fa-solid fa-database"></i> Postings List Data Structure</div>
                    <div class="card-body">
                        Each stemmed term maps to a postings dictionary:<br/><br/>
                        <code>'execut': {<br/>
                        &nbsp;&nbsp;'D08': [(s:14, w:3), (s:42, w:11)],<br/>
                        &nbsp;&nbsp;'D14': [(s:5, w:12)],<br/>
                        &nbsp;&nbsp;'D24': [(s:112, w:7), (s:115, w:2)]<br/>
                        }</code><br/><br/>
                        • <b>Document Frequency (DF):</b> Number of judgments containing term.<br/>
                        • <b>Term Frequency (TF):</b> Occurrence count per judgment.
                    </div>
                </div>
                <div class="card card-gold">
                    <div class="card-title" style="color:#FBBF24;"><i class="fa-solid fa-list-check"></i> Index Properties (Pipeline A)</div>
                    <div class="card-body">
                        • <b>Indexed Stems:</b> 8,355 unique vocabulary terms.<br/>
                        • <b>Storage Mode:</b> In-memory Python hash table with JSON persistence (`inverted_index.json`).<br/>
                        • <b>Phrase Matching Algorithm:</b> Positional merge requiring $pos(w_2) = pos(w_1) + 1$.<br/>
                        • <b>Latency:</b> 0.14 ms average query execution.
                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 11: Phrase Matching via Positional Merge -->
        <div class="slide" data-speaker="Shreerenu: Baseline & Pipeline A" data-notes="To search for a phrase in Pipeline A, like 'anticipatory bail', we must perform a positional merge. We load postings for 'anticipatori' and postings for 'bail', and check if bail immediately follows anticipatori. This works, but it requires coordinate joins across multiple terms.">
            <div class="slide-tag">Module 4 · Information Retrieval</div>
            <div class="slide-title">Phrase Matching via Positional Coordinate Merge</div>
            <div class="slide-subtitle">How Pipeline A resolves quoted multi-word phrase queries across stemmed postings.</div>

            <div class="card card-blue">
                <div class="card-title" style="color:#60A5FA;">The Positional Adjacency Verification Condition:</div>
                <div class="card-body" style="font-size:0.95rem; text-align:center;">
                    $$\text{Match in Document } d \iff \exists p \text{ such that } p \in \text{Postings}(w_1)[d] \land (p+1) \in \text{Postings}(w_2)[d]$$
                </div>
            </div>

            <div class="card card-gold" style="margin-top:14px;">
                <div class="card-title" style="color:#FBBF24;">Example: Searching for <code>"anticipatory bail"</code> in Pipeline A</div>
                <div class="card-body">
                    1. Query is stemmed: <code>"anticipatori bail"</code><br/>
                    2. Load Postings for <code>'anticipatori'</code> in D07: offsets <code>[45, 112, 230]</code><br/>
                    3. Load Postings for <code>'bail'</code> in D07: offsets <code>[46, 89, 113, 231]</code><br/>
                    4. Check adjacency: $45+1=46$ (Match!), $112+1=113$ (Match!), $230+1=231$ (Match!)<br/>
                    5. Document D07 retrieved! <b>Bottleneck:</b> Requires loading multiple postings lists and running $O(N+M)$ coordinate intersections.
                </div>
            </div>
        </div>

        <!-- SLIDE 12: Pipeline A Critical Failure Analysis (2 Real Bottleneck Examples) -->
        <div class="slide" data-speaker="Shreerenu: Baseline & Pipeline A" data-notes="Now, look at the critical bottlenecks I uncovered in Pipeline A. We have two prominent examples. First, the classic execution vs executive collision, where Porter conflates decree enforcement with executive magistrate, causing 8 false positives and plunging precision to 38.5%. Second, the suit vs suitable collision, where civil title lawsuits are conflated with employment adjectives, causing 7 false positives and 58.8% precision. Lavanya and Raju will now show how Pipeline B completely eliminates these bottlenecks.">
            <div class="slide-tag">Failure Analysis · Pipeline A Vulnerabilities</div>
            <div class="slide-title">The Over-Stemming Bottlenecks in Pipeline A: Two Failure Cases</div>
            <div class="slide-subtitle">Demonstrating why algorithmic suffix stripping collapses legal precision on Indian jurisprudence.</div>

            <div class="grid-2">
                <div class="card card-red">
                    <div class="card-title" style="color:#F87171;"><i class="fa-solid fa-scale-unbalanced"></i> Bottleneck 1: <code>execution</code> vs. <code>executive</code></div>
                    <div class="card-body">
                        • <b>Concept 1:</b> Enforcement of money decree / death warrant.<br/>
                        • <b>Concept 2:</b> Executive magistrate / detention powers under CrPC.<br/>
                        • <b>Porter Stemmer:</b> Truncates both to identical stem <code>execut</code>!<br/><br/>
                        <b>Query:</b> <code>"executive"</code><br/>
                        • Total Retrieved: 13 Judgments<br/>
                        • True Relevant Cases: 5 (D09, D14, D18, D20, D23)<br/>
                        • False Positives: <b>8 judgments</b> (decree cases in D24, D25, D01)<br/>
                        • <b>Precision: <span style="color:#EF4444; font-weight:800;">38.5% (Dismal!)</span></b>
                    </div>
                </div>
                <div class="card card-red">
                    <div class="card-title" style="color:#F87171;"><i class="fa-solid fa-gavel"></i> Bottleneck 2: <code>suit</code> vs. <code>suitable</code></div>
                    <div class="card-body">
                        • <b>Concept 1:</b> Civil partition lawsuit or money suit under CPC.<br/>
                        • <b>Concept 2:</b> Adjective 'suitable' in employment / accommodation.<br/>
                        • <b>Porter Stemmer:</b> Strips both <code>suit</code> & <code>suitable</code> to <code>suit</code>!<br/><br/>
                        <b>Query:</b> <code>"suit"</code><br/>
                        • Total Retrieved: 17 Judgments<br/>
                        • True Relevant Cases: 10 civil partition/money suits<br/>
                        • False Positives: <b>7 judgments</b> (service/employment cases)<br/>
                        • <b>Precision: <span style="color:#EF4444; font-weight:800;">58.8% (Flooded with noise!)</span></b>
                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 13: Transition to Pipeline B -->
        <div class="slide" data-speaker="Lavanya: Domain NLP Innovations" data-notes="Hello Ma'am. I am Lavanya. Seeing the failures identified by Brunda and Shreerenu—citation fragmentation, POS errors, and over-stemming—I developed the domain NLP components for Pipeline B: the Custom Legal Regex Tokenizer, Custom POS Tagging with Machine Learning, and Legal Named Entity Recognition.">
            <div class="slide-tag">Paradigm Shift · Engineering Pipeline B</div>
            <div class="slide-title">The Solution: Legal-Domain-Optimized Architecture</div>
            <div class="slide-subtitle">Transitioning from generic baseline processing to domain-preserving legal NLP engineering.</div>

            <div class="grid-3">
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-code"></i> Custom Legal Regex</div>
                    <div class="card-body">
                        Preserves statutory sections, constitutional articles, currency, and Latin maxims as <b>atomic, single tokens</b>.
                    </div>
                </div>
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-brain"></i> ML POS Classifier</div>
                    <div class="card-body">
                        Trained a <b>Logistic Regression POS Classifier</b> (76.7% accuracy) resolving Penn Treebank errors on legal court idioms.
                    </div>
                </div>
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-tags"></i> Legal NER Engine</div>
                    <div class="card-body">
                        Extracts domain entities (<code>LEGAL_SECTION</code>, <code>LEGAL_STATUTE</code>, <code>LEGAL_COURT</code>) with interactive UI filtering.
                    </div>
                </div>
            </div>
            <div class="callout-box callout-success" style="margin-top:14px;">
                <b>Engineering Philosophy:</b> "Preserve legal semantics at the token level, eliminating expensive downstream repairs."
            </div>
        </div>

        <!-- SLIDE 14: Custom Legal Regular Expressions -->
        <div class="slide" data-speaker="Lavanya: Domain NLP Innovations" data-notes="I engineered the Custom Legal Regex Tokenizer. It uses prioritized regex patterns: sections like Section 302 IPC, Indian rupees with commas, Latin maxims like suo motu, and court abbreviations. This prevents citations from being shattered.">
            <div class="slide-tag">Module 2 · Custom Tokenizer</div>
            <div class="slide-title">Custom Legal Regular Expressions (Pipeline B)</div>
            <div class="slide-subtitle">Prioritized regular expression cascades preserving statutory compounds as atomic units.</div>

            <div class="grid-2">
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-list-ol"></i> Cascaded Regex Patterns</div>
                    <div class="card-body">
                        1. <b>Sections:</b> <code>(?:Section|Sec\.|Article|Art\.)\s+\d+[A-Z]?(?:\(\d+\))*</code><br/>
                        2. <b>Monetary:</b> <code>(?:₹|Rs\.?)\s*[\d,]+(?:\/-)?</code><br/>
                        3. <b>Latin Maxims:</b> <code>(?i)\b(?:suo\s+motu|mens\s+rea|habeas\s+corpus|prima\s+facie)\b</code><br/>
                        4. <b>Statutes:</b> <code>(?:IPC|CrPC|CPC|NDPS|PMLA|NIA|POCSO|IT\s+Act)</code>
                    </div>
                </div>
                <div class="card card-blue">
                    <div class="card-title" style="color:#60A5FA;"><i class="fa-solid fa-arrow-right-arrow-left"></i> Tokenization Comparison</div>
                    <div class="card-body">
                        <b>Input:</b> <i>"Bail under Section 438 CrPC of ₹50,000/-"</i><br/><br/>
                        • <b>Pipeline A (NLTK):</b><br/>
                        <code>['Bail', 'under', 'Section', '438', 'CrPC', 'of', '₹', '50,000', '/', '-']</code> (10 tokens)<br/><br/>
                        • <b>Pipeline B (Custom Regex):</b><br/>
                        <code>['Bail', 'under', 'Section 438 CrPC', 'of', '₹50,000/-']</code> (5 tokens 🎯)
                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 15: Penn Treebank Syntax Failures & Custom Legal POS Tagging (With Ground Truth) -->
        <div class="slide" data-speaker="Lavanya: Domain NLP Innovations" data-notes="Next, look at syntactic tagging. Standard Penn Treebank taggers fail on legal terminology because they are trained on Wall Street Journal news. For example, 'learned counsel' is tagged as a past verb, and 'quashing' is tagged as a participle. Our custom legal tagger maps them to their true ground truth legal syntactic roles.">
            <div class="slide-tag">Module 2 · Syntax & Grammatical Roles</div>
            <div class="slide-title">Penn Treebank Syntax Failures vs. Custom Legal POS Tagging</div>
            <div class="slide-subtitle">Resolving systemic POS classification errors with ground truth legal syntax verification.</div>

            <table class="pres-table">
                <tr>
                    <th>Legal Syntax Sample (Corpus)</th>
                    <th>Target Word</th>
                    <th>NLTK Default Tag</th>
                    <th>Custom Legal POS</th>
                    <th>Ground Truth Role in Judgments</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td><i>"The <b>learned</b> counsel argued..."</i></td>
                    <td><code>learned</code></td>
                    <td><code>VBN</code> (Past Verb) ❌</td>
                    <td><code>JJ</code> (Adjective) ✅</td>
                    <td><b>Honorific Adjective</b> modifying counsel</td>
                    <td>Fixed ✅</td>
                </tr>
                <tr>
                    <td><i>"Petitioner sought <b>quashing</b> of FIR"</i></td>
                    <td><code>quashing</code></td>
                    <td><code>VBG</code> (Participle Verb) ❌</td>
                    <td><code>NN</code> (Noun) ✅</td>
                    <td><b>Substantive Legal Remedy Noun</b> (CrPC 482)</td>
                    <td>Fixed ✅</td>
                </tr>
                <tr>
                    <td><i>"Court took <b>suo motu</b> cognizance"</i></td>
                    <td><code>suo</code></td>
                    <td><code>NN</code> (Noun) ❌</td>
                    <td><code>RB</code> (Adverb) ✅</td>
                    <td><b>Adverbial Motion Modifier</b> ("on own motion")</td>
                    <td>Fixed ✅</td>
                </tr>
                <tr>
                    <td><i>"The <b>bench</b> dismissed appeal"</i></td>
                    <td><code>bench</code></td>
                    <td><code>NN</code> (Seat) ❌</td>
                    <td><code>NNP</code> (Judicial Panel) ✅</td>
                    <td><b>Judicial Institution</b> / Division Bench</td>
                    <td>Fixed ✅</td>
                </tr>
                <tr>
                    <td><i>"Granted <b>ad-interim</b> bail"</i></td>
                    <td><code>ad-interim</code></td>
                    <td><code>NN</code> (Split/Unknown) ❌</td>
                    <td><code>JJ</code> (Adjective) ✅</td>
                    <td><b>Interlocutory Order Modifier</b></td>
                    <td>Fixed ✅</td>
                </tr>
            </table>
        </div>

        <!-- SLIDE 16: Supervised ML POS Classifier (3 Real Project Examples) -->
        <div class="slide" data-speaker="Lavanya: Domain NLP Innovations" data-notes="Beyond rules, I trained a Supervised Machine Learning POS Classifier using Logistic Regression. I extracted contextual features: character suffixes, prefixes, orthographic flags, and neighboring words. Here are three concrete examples from our project showing how the ML classifier correctly classified learned, quashing, and ad-interim with high probability, achieving 76.7% test accuracy and 0.705 F1-score!">
            <div class="slide-tag">Module 2 · Machine Learning Classifier</div>
            <div class="slide-title">Supervised ML POS Classifier: 3 Real Legal Case Results</div>
            <div class="slide-subtitle">Multi-class Logistic Regression with contextual n-gram features evaluated on Indian court text.</div>

            <div class="grid-2">
                <div class="card card-blue">
                    <div class="card-title" style="color:#60A5FA;"><i class="fa-solid fa-microchip"></i> 3 Real Project Classification Results</div>
                    <div class="card-body">
                        • <b>Case 1:</b> <i>"The <b>learned</b> counsel for appellant"</i><br/>
                        Features: <code>word[-2:]='ed'</code>, <code>next='counsel'</code>, <code>prev='The'</code><br/>
                        Penn Treebank: <code>VBD</code> (Verb past) &rarr; <b>ML POS: <code>JJ</code> (Adjective, P=0.882) ✅</b><br/><br/>
                        • <b>Case 2:</b> <i>"remedy of <b>quashing</b> of FIR"</i><br/>
                        Features: <code>word[-3:]='ing'</code>, <code>next='of'</code>, <code>prev='remedy'</code><br/>
                        Penn Treebank: <code>VBG</code> (Verb active) &rarr; <b>ML POS: <code>NN</code> (Noun, P=0.914) ✅</b><br/><br/>
                        • <b>Case 3:</b> <i>"grant of <b>ad-interim</b> injunction"</i><br/>
                        Features: <code>has_hyphen=True</code>, <code>next='injunction'</code><br/>
                        Penn Treebank: <code>NN</code> / Split &rarr; <b>ML POS: <code>JJ</code> (Adjective, P=0.847) ✅</b>
                    </div>
                </div>
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-chart-line"></i> Held-Out Empirical Test Results</div>
                    <div class="card-body">
                        <div class="kpi-container" style="margin-top:0;">
                            <div class="kpi-badge">
                                <div class="kpi-val" style="color:#10B981;">76.7%</div>
                                <div class="kpi-label">Test Accuracy</div>
                            </div>
                            <div class="kpi-badge">
                                <div class="kpi-val" style="color:#60A5FA;">0.705</div>
                                <div class="kpi-label">Weighted F1-Score</div>
                            </div>
                        </div>
                        <div style="margin-top:10px; font-size:0.82rem;">
                            • <b>Algorithm:</b> Multi-Class Logistic Regression with L2 regularization.<br/>
                            • <b>Feature Space:</b> Prefixes (2-3), Suffixes (2-4), Context words, Title/Upper flags.<br/>
                            • <b>Test Split:</b> 20% held-out annotated court sentences.<br/>
                            • Successfully generalizes across Indian judicial drafting styles.
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 17: Named Entity Recognition in Case Law -->
        <div class="slide" data-speaker="Lavanya: Domain NLP Innovations" data-notes="I also implemented domain-specific Named Entity Recognition. Legal text requires knowing not just who the person is, but which Section was invoked and which Court ruled. Our NER pipeline extracts LEGAL_SECTION, LEGAL_STATUTE, LEGAL_COURT, and LEGAL_CITATION.">
            <div class="slide-tag">Module 2 · Named Entity Extraction</div>
            <div class="slide-title">Named Entity Recognition (NER) in Indian Case Law</div>
            <div class="slide-subtitle">Extracting domain statutory entities alongside standard linguistic categories with ground truth matching.</div>

            <div class="grid-2">
                <div class="card card-blue">
                    <div class="card-title" style="color:#60A5FA;"><i class="fa-solid fa-tags"></i> Domain-Specific Legal Entities</div>
                    <div class="card-body">
                        • <code>LEGAL_SECTION</code>: <i>Section 438 CrPC</i>, <i>Section 302 IPC</i>, <i>s. 135 Customs</i><br/>
                        • <code>LEGAL_STATUTE</code>: <i>Code of Criminal Procedure</i>, <i>NDPS Act</i>, <i>PMLA 2002</i><br/>
                        • <code>LEGAL_COURT</code>: <i>Supreme Court of India</i>, <i>High Court of Allahabad</i><br/>
                        • <code>LEGAL_CITATION</code>: <i>AIR 2020 SC 123</i>, <i>(2021) 4 SCC 302</i>
                    </div>
                </div>
                <div class="card card-gold">
                    <div class="card-title" style="color:#FBBF24;"><i class="fa-solid fa-user-group"></i> Standard Linguistic Entities</div>
                    <div class="card-body">
                        • <code>PERSON</code>: Accused, Petitioners, Respondents, Learned Judges<br/>
                        • <code>ORG</code>: Enforcement Directorate (ED), Central Bureau of Investigation (CBI)<br/>
                        • <code>MONEY</code>: Bail surety bonds, fine penalties (<i>₹50,000/-</i>)<br/>
                        • <code>GPE</code>: State of U.P., State of Karnataka, UT of J&K
                    </div>
                </div>
            </div>
            <div class="callout-box callout-success" style="margin-top:12px;">
                <b>Interactive Visualizer:</b> Built into our Streamlit GUI, allowing users to select any judgment (D01–D25) and filter entity tags dynamically with color-coded highlighting.
            </div>
        </div>

        <!-- SLIDE 18: N-Gram Collocations & BPE Subwords -->
        <div class="slide" data-speaker="Lavanya: Domain NLP Innovations" data-notes="Finally, I extracted 1-to-5 grams and trained a Byte Pair Encoding model. The N-grams prove that legal text is dominated by formulaic multi-word phrases like 'code of criminal procedure' and 'anticipatory bail'. BPE with 6,000 subwords solves out-of-vocabulary terms like 'unconstitutional'. Raju will now present Pipeline B integration, dual-level indexing, and evaluation.">
            <div class="slide-tag">Module 2 · Lexical Analysis & Subwords</div>
            <div class="slide-title">Statistical N-Grams & BPE Subword Tokenization</div>
            <div class="slide-subtitle">Empirical evidence of legal collocations and handling out-of-vocabulary terminology.</div>

            <div class="grid-2">
                <div class="card card-blue">
                    <div class="card-title" style="color:#60A5FA;"><i class="fa-solid fa-layer-group"></i> Higher-Order Legal N-Grams</div>
                    <div class="card-body">
                        • <b>Bigrams:</b> <code>high court</code> (1,842), <code>learned counsel</code> (1,650), <code>anticipatory bail</code> (432)<br/>
                        • <b>Trigrams:</b> <code>learned counsel for</code> (1,210), <code>code of criminal</code> (480)<br/>
                        • <b>4-Grams:</b> <code>code of criminal procedure</code> (245), <code>learned counsel for the</code> (389)<br/>
                        • <b>5-Grams:</b> <code>under section of criminal procedure</code> (112)
                    </div>
                </div>
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-puzzle-piece"></i> BPE Subword Segmentation (6,000 Vocab)</div>
                    <div class="card-body">
                        BPE breaks rare or hyphenated legal words into known subword units without defaulting to <code>&lt;UNK&gt;</code>:<br/><br/>
                        • <code>unconstitutional</code> &rarr; <code>un + constitution + al</code><br/>
                        • <code>non-bailable</code> &rarr; <code>non + - + bail + able</code><br/>
                        • <code>misappropriation</code> &rarr; <code>mis + appropria + tion</code>
                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 19: Contextual Lemmatization (3 Concrete Failure vs Victory Examples) -->
        <div class="slide" data-speaker="Raju: Pipeline B & IR Evaluation" data-notes="Thank you Lavanya. I am Raju. I engineered Pipeline B, built the dual-level index, the multi-mode IR engine, and conducted the benchmark evaluation. First, look at how contextual lemmatization resolves the stemmer collisions that Shreerenu exposed. We have three concrete examples: execution vs executive, suit vs suitable, and learned vs learning. In every single case, POS lemmatization preserves distinct semantic lemmas, achieving 100% precision!">
            <div class="slide-tag">Module 2 · Morphological Solution</div>
            <div class="slide-title">Contextual POS-Aware Lemmatization: 3 Collision Resolutions</div>
            <div class="slide-subtitle">How Pipeline B achieves 100% precision on terms that caused Porter stemming to collapse.</div>

            <div class="grid-3">
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-check"></i> Case 1: <code>execution</code> / <code>executive</code></div>
                    <div class="card-body">
                        • <b>Pipeline A (Porter):</b> Both &rarr; <code>execut</code><br/>
                        Query <code>"executive"</code>: 8 false positives.<br/>
                        <b>Precision: 38.5% ❌</b><br/><br/>
                        • <b>Pipeline B (POS Lemma):</b><br/>
                        <code>execution</code> [NN] &rarr; <code>execution</code><br/>
                        <code>executive</code> [JJ/NN] &rarr; <code>executive</code><br/>
                        Query <code>"executive"</code>: 5 true cases.<br/>
                        <b>Precision: 100.0% 🏆</b>
                    </div>
                </div>
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-check"></i> Case 2: <code>suit</code> / <code>suitable</code></div>
                    <div class="card-body">
                        • <b>Pipeline A (Porter):</b> Both &rarr; <code>suit</code><br/>
                        Query <code>"suit"</code>: 7 false positives from employment cases.<br/>
                        <b>Precision: 58.8% ❌</b><br/><br/>
                        • <b>Pipeline B (POS Lemma):</b><br/>
                        <code>suit</code> [NN] &rarr; <code>suit</code><br/>
                        <code>suitable</code> [JJ] &rarr; <code>suitable</code><br/>
                        Query <code>"suit"</code>: Only real civil suits.<br/>
                        <b>Precision: 100.0% 🏆</b>
                    </div>
                </div>
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-check"></i> Case 3: <code>learned</code> / <code>learning</code></div>
                    <div class="card-body">
                        • <b>Pipeline A (Porter):</b> <code>learned</code> &rarr; <code>learn</code><br/>
                        Destroys judicial honorific; conflates court citations with academic education.<br/><br/>
                        • <b>Pipeline B (POS Lemma):</b><br/>
                        <code>learned</code> [JJ] &rarr; <code>learned</code> (honorific intact!)<br/>
                        <code>learning</code> [VBG] &rarr; <code>learn</code> (verb normalized)<br/>
                        <b>Precision: 100.0% 🏆</b>
                    </div>
                </div>
            </div>
            <div class="callout-box callout-success" style="margin-top:12px;">
                <b>Linguistic Rationale:</b> WordNet and spaCy lemmatizers consult grammatical dictionary lemmas conditioned on part-of-speech tags, ensuring that legal nouns and adjectives never lose their unique semantic identity.
            </div>
        </div>

        <!-- SLIDE 20: Dual-Level Atomic Positional Indexing -->
        <div class="slide" data-speaker="Raju: Pipeline B & IR Evaluation" data-notes="I architected Pipeline B's dual-level index. Instead of only indexing single words, it indexes atomic compound keys like 'Section 302 IPC' and 'anticipatory bail' directly, while also keeping individual lemmas. That means searching for a statutory section is a direct O(1) hash lookup. It runs in 0.04 ms—3.5 times faster than Pipeline A!">
            <div class="slide-tag">Module 3 · Inverted Index Innovation</div>
            <div class="slide-title">Dual-Level Atomic Positional Indexing</div>
            <div class="slide-subtitle">Sub-millisecond retrieval through dual-layer posting structures in Pipeline B.</div>

            <div class="grid-2">
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-layer-group"></i> Layer 1: Atomic Compound Postings</div>
                    <div class="card-body">
                        Indexes intact multi-word legal terms as single keys:<br/><br/>
                        <code>'section 302 ipc': {<br/>
                        &nbsp;&nbsp;'D11': [14, 82],<br/>
                        &nbsp;&nbsp;'D12': [5],<br/>
                        &nbsp;&nbsp;'D18': [23, 91]<br/>
                        }</code><br/><br/>
                        • Bypasses multi-word coordinate intersections.<br/>
                        • Direct $O(1)$ hash lookup in memory!
                    </div>
                </div>
                <div class="card card-blue">
                    <div class="card-title" style="color:#60A5FA;"><i class="fa-solid fa-font"></i> Layer 2: Constituent Lemma Postings</div>
                    <div class="card-body">
                        Indexes individual lemmatized tokens with sentence and word offsets for general flexible search:<br/><br/>
                        • Total Indexed Terms: <b>9,005 terms</b> (+650 compound legal entities over Pipeline A).<br/>
                        • <b>Average Latency:</b> <span style="color:#10B981; font-weight:800; font-size:1.1rem;">0.04 ms</span> (vs. 0.14 ms in Pipeline A).<br/>
                        • <b>Speedup Factor:</b> <b>3.5× Faster!</b>
                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 21: Pipeline B Architecture Diagram (Clean Vector Flowchart) -->
        <div class="slide" data-speaker="Raju: Pipeline B & IR Evaluation" data-notes="Here is the complete architectural flowchart of Pipeline B that I assembled. It integrates domain cleaning, custom legal tokenization, protected stopwords, POS lemmatization, custom POS tagging, and dual-level indexing. Notice our green optimization badges showing why this is our winning model.">
            <div class="slide-tag">Module 3 · Best Model Architecture</div>
            <div class="slide-title">Pipeline B: Legal-Domain-Optimized Architecture (Best Model 🏆)</div>
            <div class="slide-subtitle">Sequential data-flow of the winning domain-optimized architecture with optimization callouts.</div>

            <div class="flowchart-wrapper">
                <div class="flowchart-row">
                    <div class="flowchart-node node-green">
                        <div class="flowchart-node-title"><i class="fa-solid fa-file-pdf"></i> Raw Judgments</div>
                        <div class="flowchart-node-desc">25 Court PDFs<br/>(257,849 tokens)</div>
                    </div>
                    <div class="flowchart-arrow">&rarr;</div>
                    <div class="flowchart-node node-green">
                        <div class="flowchart-node-title"><i class="fa-solid fa-shield-halved"></i> Domain Cleaning</div>
                        <div class="flowchart-node-desc">De-hyphenation,<br/>statutory preservation</div>
                    </div>
                    <div class="flowchart-arrow">&rarr;</div>
                    <div class="flowchart-node node-green">
                        <div class="flowchart-node-title"><i class="fa-solid fa-code"></i> Custom Regex Tokenizer</div>
                        <div class="flowchart-node-desc">Atomic citations,<br/>currency & maxims</div>
                    </div>
                    <div class="flowchart-arrow">&rarr;</div>
                    <div class="flowchart-node node-green">
                        <div class="flowchart-node-title"><i class="fa-solid fa-shield-virus"></i> Protected Stopwords</div>
                        <div class="flowchart-node-desc">8 Negation Whitelist<br/>(49.9% compression)</div>
                    </div>
                    <div class="flowchart-arrow">&rarr;</div>
                    <div class="flowchart-node node-green">
                        <div class="flowchart-node-title"><i class="fa-solid fa-book-bookmark"></i> POS Lemmatization</div>
                        <div class="flowchart-node-desc">WordNet/spaCy<br/>Contextual lemmas</div>
                    </div>
                    <div class="flowchart-arrow">&rarr;</div>
                    <div class="flowchart-node node-green">
                        <div class="flowchart-node-title"><i class="fa-solid fa-layer-group"></i> Dual-Level Index</div>
                        <div class="flowchart-node-desc">Atomic keys + lemmas<br/>(9,005 terms)</div>
                    </div>
                    <div class="flowchart-arrow">&rarr;</div>
                    <div class="flowchart-node node-green">
                        <div class="flowchart-node-title"><i class="fa-solid fa-trophy"></i> Multi-Mode Engine</div>
                        <div class="flowchart-node-desc">Boolean & TF-IDF<br/>Mean F1: 0.7979 🏆</div>
                    </div>
                </div>

                <div class="flowchart-callouts">
                    <div class="callout-box callout-success" style="margin:0;">
                        <b>✅ Atomic Citations Retained:</b> <code>Section 302 IPC</code> and <code>₹50,000/-</code> kept as intact single keys in the index.
                    </div>
                    <div class="callout-box callout-success" style="margin:0;">
                        <b>✅ Zero Semantic Collisions:</b> <code>execution</code> and <code>executive</code> kept distinct, achieving 100% precision.
                    </div>
                    <div class="callout-box callout-success" style="margin:0;">
                        <b>✅ Sub-Millisecond Speed:</b> Direct $O(1)$ compound term lookup runs in 0.04 ms (3.5× faster than Pipeline A).
                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 22: Dual-Level Index vs. Conventional Merge (A Concrete Walkthrough Example) -->
        <div class="slide" data-speaker="Raju: Pipeline B & IR Evaluation" data-notes="Let us look at how the Dual-Level Index and our multi-mode engine work with concrete examples. Consider the query 'Section 302 IPC'. In Pipeline A, the engine must load three separate postings lists for 'section', '302', and 'ipc', and run an iterative coordinate check. In Pipeline B, 'section 302 ipc' is already a single atomic key in Layer 1. A single O(1) dictionary lookup retrieves all relevant judgments in 0.04 ms—3.5 times faster! For Boolean queries, our Shunting-Yard parser evaluates 'anticipatory bail AND NOT murder' through set differences, and Vector Space scores terms via length-normalized TF-IDF Cosine similarity.">
            <div class="slide-tag">Module 4 · Information Retrieval Architecture</div>
            <div class="slide-title">Dual-Level Index vs. Conventional Merge: Concrete Query Walkthrough</div>
            <div class="slide-subtitle">Demonstrating execution mechanics for <code>"Section 302 IPC"</code> and Multi-Mode Boolean/Ranked Search.</div>

            <div class="grid-2">
                <div class="card card-red">
                    <div class="card-title" style="color:#F87171;"><i class="fa-solid fa-clock-rotate-left"></i> Pipeline A: Positional Coordinate Merge</div>
                    <div class="card-body">
                        <b>Query:</b> <code>"Section 302 IPC"</code><br/>
                        1. Fetch Postings(<code>'section'</code>): 1,420 positions in 22 docs.<br/>
                        2. Fetch Postings(<code>'302'</code>): 412 positions in 8 docs.<br/>
                        3. Fetch Postings(<code>'ipc'</code>): 890 positions in 19 docs.<br/>
                        4. <b>Coordinate Iteration:</b> Checks if $pos(302) = pos(\text{section}) + 1$ and $pos(\text{ipc}) = pos(302) + 1$.<br/>
                        • Complexity: $O(P_1 + P_2 + P_3)$ operations.<br/>
                        • <b>Query Latency:</b> <span style="color:#EF4444; font-weight:800;">0.14 ms</span>
                    </div>
                </div>
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-bolt"></i> Pipeline B: Direct Atomic Hash Lookup</div>
                    <div class="card-body">
                        <b>Query:</b> <code>"Section 302 IPC"</code><br/>
                        1. Direct Key Lookup: <code>index['section 302 ipc']</code><br/>
                        2. Postings returned instantly:<br/>
                        &nbsp;&nbsp;<code>{'D11': [14, 82], 'D12': [5], 'D18': [23, 91]}</code><br/>
                        • Zero coordinate intersection needed!<br/>
                        • Complexity: <b>$O(1)$ Hash Table Access</b>.<br/>
                        • <b>Query Latency:</b> <span style="color:#10B981; font-weight:800;">0.04 ms (3.5× Faster! ⚡)</span>
                    </div>
                </div>
            </div>

            <div class="card card-gold" style="margin-top:12px;">
                <div class="card-title" style="color:#FBBF24;"><i class="fa-solid fa-sliders"></i> Multi-Mode IR Engine Capabilities</div>
                <div class="card-body">
                    • <b>Boolean Shunting-Yard:</b> <code>"anticipatory bail" AND NOT murder</code> &rarr; Postings(<code>anticipatory bail</code>) $\setminus$ Postings(<code>murder</code>) &rarr; Retrieves D07, D09, D14.<br/>
                    • <b>Vector Space (TF-IDF Cosine):</b> $\text{TF-IDF}(t,d) = (1 + \log \text{TF}_{t,d}) \times \log(N/\text{DF}_t)$, length-normalized against document vector.
                </div>
            </div>
        </div>

        <!-- SLIDE 23: Controlled Evaluation Across 15 Benchmark Queries (Fitted Layout) -->
        <div class="slide" data-speaker="Raju: Pipeline B & IR Evaluation" data-notes="Here is the quantitative proof from our 15 benchmark queries. Notice the side-by-side layout: on the left, our empirical metrics table; on the right, the high-resolution comparison chart. Pipeline B is the clear, undisputed winner: Mean Precision improves from 0.7089 to 0.7721 (+8.9%), Mean F1-score increases from 0.7549 to 0.7979 (+5.7%), Precision@5 reaches 0.8111 (+9.0%), and Latency drops to 0.04 ms (3.5x faster), while retaining 100% of the recall.">
            <div class="slide-tag">Module 5 · Controlled Evaluation</div>
            <div class="slide-title">Empirical Benchmark Evaluation (15 Legal Queries)</div>
            <div class="slide-subtitle">Rigorous head-to-head comparison proving Pipeline B's decisive superiority.</div>

            <div class="grid-2" style="align-items: center; gap: 20px;">
                <div>
                    <table class="pres-table">
                        <tr>
                            <th>Evaluation Measure</th>
                            <th>Pipeline A (Baseline)</th>
                            <th>Pipeline B (Legal Optimized)</th>
                            <th>Empirical Margin</th>
                            <th>Winning Model</th>
                        </tr>
                        <tr>
                            <td><b>Mean Precision</b></td>
                            <td>0.7089</td>
                            <td><b>0.7721</b></td>
                            <td><span style="color:#10B981; font-weight:700;">+8.9% Precision Boost</span></td>
                            <td><b>Pipeline B 🏆</b></td>
                        </tr>
                        <tr>
                            <td><b>Mean Recall</b></td>
                            <td>0.8904</td>
                            <td><b>0.8904</b></td>
                            <td>100% Recall Retained</td>
                            <td>Tie</td>
                        </tr>
                        <tr>
                            <td><b>Mean F1-Score</b></td>
                            <td>0.7549</td>
                            <td><b>0.7979</b></td>
                            <td><span style="color:#10B981; font-weight:700;">+5.7% Harmonic Gain</span></td>
                            <td><b>Pipeline B 🏆</b></td>
                        </tr>
                        <tr>
                            <td><b>Precision@5 (Top-Ranked)</b></td>
                            <td>0.7444</td>
                            <td><b>0.8111</b></td>
                            <td><span style="color:#10B981; font-weight:700;">+9.0% Density Improvement</span></td>
                            <td><b>Pipeline B 🏆</b></td>
                        </tr>
                        <tr>
                            <td><b>Query Latency</b></td>
                            <td>0.14 ms</td>
                            <td><b>0.04 ms</b></td>
                            <td><span style="color:#10B981; font-weight:700;">3.5× Faster Execution</span></td>
                            <td><b>Pipeline B 🏆</b></td>
                        </tr>
                    </table>

                    <div class="callout-box callout-success" style="margin-top:12px;">
                        <b>Key Empirical Finding:</b> Pipeline B improves precision without sacrificing recall, proving that domain-preserving tokenization and contextual lemmatization cleanly eliminate false positives.
                    </div>
                </div>

                <div>
                    <div class="slide-img-container" style="max-height:360px; background:#0B0F19; border: 1px solid var(--card-border); padding: 8px;">
                        <img src="chart_pipeline_metrics.png" alt="Pipeline Comparison Bar Chart" style="max-height:340px; width:100%; object-fit:contain;">
                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 24: Interactive Dashboard GUI & Live Demo -->
        <div class="slide" data-speaker="Raju: Pipeline B & IR Evaluation" data-notes="We built a complete 17-page Streamlit dashboard in a professional dark navy theme. Notice our special feature: on any query—like 'smuggl' or 'bail'—it displays live Precision, Recall, and F1-score metric cards along with the academic forensic execution trace right above the retrieved judgments. I will now open the live demo.">
            <div class="slide-tag">Module 6 · GUI Implementation & Live Demo</div>
            <div class="slide-title">Interactive Streamlit GUI & Live Evaluation Telemetry</div>
            <div class="slide-subtitle">A modern dark navy legal-tech analytics dashboard with real-time IR metric calculation.</div>

            <div class="grid-2">
                <div class="card card-blue">
                    <div class="card-title" style="color:#60A5FA;"><i class="fa-solid fa-desktop"></i> Dashboard Architecture (17 Views)</div>
                    <div class="card-body">
                        • <b>Corpus:</b> Dashboard Overview, Document Explorer, Corpus Statistics.<br/>
                        • <b>NLP Analysis:</b> Tokenizer Workbench, Stopword Policy, Stem/Lemma Table, Custom POS & ML, Legal NER Visualizer, N-Grams, BPE Subwords.<br/>
                        • <b>Information Retrieval:</b> Flagship Search, Positional Index Explorer, Boolean Builder, Pipeline A vs B Comparison, Retrieval Evaluation.
                    </div>
                </div>
                <div class="card card-green">
                    <div class="card-title" style="color:#34D399;"><i class="fa-solid fa-bolt"></i> Live Real-Time IR Evaluation Engine</div>
                    <div class="card-body">
                        • <b>Instant Metric Cards:</b> Precision, Recall, F1-Score, Precision@5, Latency dynamically calculated on ANY query.<br/>
                        • <b>Forensic IR Execution Trace:</b> Academic monospace log showing Query terms, Postings verification, TP, FP, FN classification.<br/>
                        • <b>Interactive Ground Truth Selector:</b> Allows professors to test custom relevance sets live!
                    </div>
                </div>
            </div>
            <div class="callout-box callout-success" style="margin-top:14px; text-align:center;">
                <b>🚀 Ready for Live Demo:</b> We will now switch to <code>http://localhost:8501</code> to demonstrate live retrieval on <i>'smuggl'</i>, <i>'bail'</i>, and <i>'executive'</i>.
            </div>
        </div>

        <!-- SLIDE 25: Conclusion & Viva Defense Punchline -->
        <div class="slide" data-speaker="All Members: Conclusion" data-notes="In conclusion, our project proves that legal NLP requires domain preservation. Protecting statutory citations as atomic units, shielding negations, and using POS-aware lemmatization is not an optional tweak—it is essential. Pipeline B is verified as the best model. Thank you Ma'am, we are ready for questions!">
            <div class="title-hero">
                <div class="slide-tag">Final Synthesis · Viva Defense Summary</div>
                <h1 style="font-size:2.1rem;">Conclusion & Final Defense Verdict</h1>
                <div class="dept" style="font-size:0.96rem; max-width:820px; margin: 0 auto 18px auto; line-height:1.6;">
                    "In legal informatics, text processing is inseparable from statutory reasoning. Generic NLP fails because citations fragment, liability inverts, and stems collide. <b>Pipeline B stands conclusively established as the Best Performing Pipeline</b>, achieving <b>0.7721 Precision</b>, <b>0.7979 F1-Score</b>, and <b>3.5× faster execution</b>."
                </div>

                <div class="grid-4" style="margin-top:18px;">
                    <div class="card card-blue" style="padding:12px; text-align:center;">
                        <div style="font-weight:700; color:#60A5FA;">👤 Brunda</div>
                        <div style="font-size:0.74rem; color:#94A3B8; margin-top:4px;">Ingestion, Cleaning & Stemming Baseline</div>
                    </div>
                    <div class="card card-gold" style="padding:12px; text-align:center;">
                        <div style="font-weight:700; color:#FBBF24;">👤 Shreerenu</div>
                        <div style="font-size:0.74rem; color:#94A3B8; margin-top:4px;">Pipeline A & Collision Analysis</div>
                    </div>
                    <div class="card card-green" style="padding:12px; text-align:center;">
                        <div style="font-weight:700; color:#34D399;">👤 Lavanya</div>
                        <div style="font-size:0.74rem; color:#94A3B8; margin-top:4px;">Custom Regex, ML POS & NER</div>
                    </div>
                    <div class="card card-green" style="padding:12px; text-align:center;">
                        <div style="font-weight:700; color:#34D399;">👤 Raju</div>
                        <div style="font-size:0.74rem; color:#94A3B8; margin-top:4px;">Pipeline B, Dual Index & IR Eval</div>
                    </div>
                </div>

                <div style="margin-top:24px;">
                    <span style="font-size:1.15rem; font-weight:700; color:#34D399;">Thank You, Ma'am! We welcome your questions.</span>
                </div>
            </div>
        </div>

    </div>

    <!-- Presenter Notes Overlay Box -->
    <div class="notes-panel" id="notesPanel">
        <div class="notes-header">
            <span>🎤 Presenter Speaking Notes</span>
            <span style="cursor:pointer;" onclick="toggleNotes()">✕</span>
        </div>
        <div id="notesContent"></div>
    </div>

    <!-- Bottom Navigation Controls -->
    <div class="pres-footer">
        <div class="controls-group">
            <button class="btn-nav" onclick="prevSlide()"><i class="fa-solid fa-chevron-left"></i> Prev</button>
            <div class="slide-counter" id="slideCounter">Slide 1 / 25</div>
            <button class="btn-nav" onclick="nextSlide()">Next <i class="fa-solid fa-chevron-right"></i></button>
        </div>

        <div style="display:flex; align-items:center; gap:16px;">
            <span style="font-size:0.76rem; color:#64748B;">Use <kbd>&larr;</kbd> <kbd>&rarr;</kbd> or <kbd>Space</kbd> to Navigate</span>
            <button class="btn-nav" onclick="toggleNotes()" title="Toggle Speaker Notes [N]"><i class="fa-solid fa-note-sticky"></i> Notes ( N )</button>
            <button class="btn-nav" onclick="toggleFullScreen()" title="Fullscreen Mode [F]"><i class="fa-solid fa-expand"></i> Fullscreen ( F )</button>
        </div>
    </div>

    <script>
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;
        const counterEl = document.getElementById('slideCounter');
        const progressBar = document.getElementById('progressBar');
        const speakerBadge = document.getElementById('speakerBadge');
        const notesPanel = document.getElementById('notesPanel');
        const notesContent = document.getElementById('notesContent');

        function updateSlide(index) {
            if (index < 0) index = 0;
            if (index >= totalSlides) index = totalSlides - 1;
            
            slides[currentSlide].classList.remove('active');
            currentSlide = index;
            slides[currentSlide].classList.add('active');

            counterEl.textContent = `Slide ${currentSlide + 1} / ${totalSlides}`;
            const progressPct = ((currentSlide + 1) / totalSlides) * 100;
            progressBar.style.width = `${progressPct}%`;

            const speaker = slides[currentSlide].getAttribute('data-speaker') || 'Presenter';
            speakerBadge.textContent = speaker;

            const notes = slides[currentSlide].getAttribute('data-notes') || 'No notes for this slide.';
            notesContent.innerHTML = notes;
        }

        function nextSlide() {
            if (currentSlide < totalSlides - 1) {
                updateSlide(currentSlide + 1);
            }
        }

        function prevSlide() {
            if (currentSlide > 0) {
                updateSlide(currentSlide - 1);
            }
        }

        function toggleNotes() {
            notesPanel.classList.toggle('active');
        }

        function toggleFullScreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.log(`Fullscreen error: ${err.message}`);
                });
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
                e.preventDefault();
                nextSlide();
            } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
                e.preventDefault();
                prevSlide();
            } else if (e.key === 'Home') {
                e.preventDefault();
                updateSlide(0);
            } else if (e.key === 'End') {
                e.preventDefault();
                updateSlide(totalSlides - 1);
            } else if (e.key === 'f' || e.key === 'F') {
                e.preventDefault();
                toggleFullScreen();
            } else if (e.key === 'n' || e.key === 'N') {
                e.preventDefault();
                toggleNotes();
            }
        });

        // Initialize first slide
        updateSlide(0);
    </script>
</body>
</html>
"""

with open("reports/Presentation.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Updated reports/Presentation.html successfully!")
