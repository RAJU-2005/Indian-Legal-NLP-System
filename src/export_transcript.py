"""
Export Antigravity Conversation Transcript to Clean Markdown and Self-Contained HTML.
"""
import json
import re
from pathlib import Path
import html

def export_conversation():
    app_data_dir = Path(r"C:\Users\Admin\.gemini\antigravity")
    conv_id = "91afb725-9ae2-4a2c-912e-a20be6bfcd46"
    log_dir = app_data_dir / "brain" / conv_id / ".system_generated" / "logs"
    
    transcript_file = log_dir / "transcript_full.jsonl"
    if not transcript_file.exists():
        transcript_file = log_dir / "transcript.jsonl"
        
    if not transcript_file.exists():
        print(f"Error: Transcript not found at {transcript_file}")
        return

    with open(transcript_file, "r", encoding="utf-8") as f:
        steps = [json.loads(line) for line in f]

    turns = []
    current_user = None
    current_assistant_replies = []

    for s in steps:
        stype = s.get("type")
        if stype == "USER_INPUT":
            if current_user is not None:
                # Filter out pure waiting status strings if a major answer exists
                final_text = ""
                major_replies = [r for r in current_assistant_replies if len(r) > 150]
                if major_replies:
                    final_text = "\n\n---\n\n".join(major_replies)
                else:
                    final_text = "\n\n".join(current_assistant_replies)
                    
                turns.append({
                    "user": current_user,
                    "assistant": final_text.strip(),
                    "timestamp": s.get("created_at", "")
                })
                current_assistant_replies = []
                
            raw_user = s.get("content", "")
            match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", raw_user, re.DOTALL)
            clean_u = match.group(1).strip() if match else raw_user.strip()
            current_user = clean_u
            
        elif stype == "PLANNER_RESPONSE":
            content = s.get("content", "").strip()
            if content and not content.startswith("Tool call:") and len(content) > 15:
                # Exclude intermediate progress waiting phrases
                if not any(content.lower().startswith(p) for p in [
                    "i will wait", "i am waiting", "i have launched", "i have started", "verifying the", "testing document"
                ]):
                    current_assistant_replies.append(content)
                elif len(content) > 250: # keep longer explanations even if started with those
                    current_assistant_replies.append(content)

    if current_user is not None:
        final_text = ""
        major_replies = [r for r in current_assistant_replies if len(r) > 150]
        if major_replies:
            final_text = "\n\n---\n\n".join(major_replies)
        else:
            final_text = "\n\n".join(current_assistant_replies)
        turns.append({
            "user": current_user,
            "assistant": final_text.strip(),
            "timestamp": ""
        })

    out_dir = Path(r"C:\Users\Admin\NLP_A1\Domain_Text_Analysis_Retrieval\reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    md_file = out_dir / "Conversation_Transcript.md"
    html_file = out_dir / "Conversation_Transcript.html"

    # 1. Generate Markdown
    md_lines = [
        "# Indian Legal Judgment Analysis & Retrieval System — Development Transcript",
        "**Project:** NLP Assessment 1 (Vidyashilp University, 2026-27)",
        f"**Conversation ID:** `{conv_id}`",
        "**System:** Google Antigravity Agentic Pair Programming",
        "\n---\n"
    ]

    for idx, turn in enumerate(turns, 1):
        u_text = turn["user"]
        a_text = turn["assistant"]
        if not u_text and not a_text:
            continue
        md_lines.append(f"## 👤 User Prompt {idx}\n")
        md_lines.append(f"```markdown\n{u_text}\n```\n" if "\n" in u_text else f"> {u_text}\n")
        md_lines.append(f"### 🤖 Antigravity Response {idx}\n")
        md_lines.append(f"{a_text}\n")
        md_lines.append("\n---\n")

    with open(md_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Markdown exported to: {md_file}")

    # 2. Generate Standalone HTML Document
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indian Legal Judgment NLP System — Development Chat Transcript</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.1/marked.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        :root {{
            --bg-color: #0A0E1A;
            --card-bg: #111827;
            --user-card-bg: #1E293B;
            --accent-blue: #3B82F6;
            --accent-gold: #D97706;
            --accent-green: #10B981;
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --border-color: #1E293B;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            padding: 24px;
        }}
        .container {{
            max-width: 1080px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #0F172A 0%, #162032 50%, #111827 100%);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--accent-blue);
            border-radius: 12px;
            padding: 28px 32px;
            margin-bottom: 32px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }}
        .header h1 {{
            font-size: 1.85rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 8px;
        }}
        .header .subtitle {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-bottom: 16px;
        }}
        .header .pills {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }}
        .pill {{
            background: rgba(59, 130, 246, 0.15);
            color: #60A5FA;
            border: 1px solid rgba(59, 130, 246, 0.35);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .pill-gold {{
            background: rgba(217, 119, 6, 0.15);
            color: #FBBF24;
            border-color: rgba(217, 119, 6, 0.35);
        }}
        .turn-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            margin-bottom: 28px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .turn-header {{
            background-color: rgba(30, 41, 59, 0.6);
            padding: 14px 24px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .turn-title {{
            font-weight: 700;
            font-size: 0.95rem;
            color: #60A5FA;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .user-section {{
            background-color: #0F172A;
            border-left: 4px solid var(--accent-gold);
            padding: 18px 24px;
            border-bottom: 1px solid var(--border-color);
        }}
        .user-label {{
            font-size: 0.78rem;
            font-weight: 700;
            color: #FBBF24;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }}
        .user-text {{
            color: #E2E8F0;
            font-size: 0.92rem;
            white-space: pre-wrap;
            word-break: break-word;
        }}
        .assistant-section {{
            padding: 24px;
            color: #E2E8F0;
            font-size: 0.95rem;
            line-height: 1.7;
        }}
        .assistant-label {{
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--accent-green);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 14px;
        }}
        .markdown-body pre {{
            background-color: #0B0F19 !important;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px;
            overflow-x: auto;
            margin: 14px 0;
        }}
        .markdown-body code {{
            font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
            font-size: 0.88rem;
        }}
        .markdown-body p {{ margin-bottom: 12px; }}
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {{
            color: #FFFFFF;
            margin-top: 18px;
            margin-bottom: 10px;
        }}
        .markdown-body table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
            font-size: 0.88rem;
        }}
        .markdown-body th, .markdown-body td {{
            border: 1px solid var(--border-color);
            padding: 10px 14px;
            text-align: left;
        }}
        .markdown-body th {{
            background-color: #1E293B;
            color: #94A3B8;
        }}
        .print-btn {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #3B82F6;
            color: #FFFFFF;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(59,130,246,0.4);
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 1000;
        }}
        .print-btn:hover {{ background: #2563EB; }}
        @media print {{
            .print-btn {{ display: none; }}
            body {{ background: #FFFFFF; color: #000000; padding: 0; }}
            .turn-card {{ border: 1px solid #CCC; box-shadow: none; page-break-inside: avoid; }}
            .header {{ border: 1px solid #CCC; }}
        }}
    </style>
</head>
<body>
    <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
    <div class="container">
        <div class="header">
            <h1>Indian Legal Judgment Analysis & Retrieval System</h1>
            <div class="subtitle">Complete Agentic Pair-Programming Conversation & Engineering Transcript</div>
            <div class="pills">
                <span class="pill">🏛️ Vidyashilp University · Assessment 1</span>
                <span class="pill pill-gold">📜 Full Development Chat History</span>
                <span class="pill">🤖 Google Antigravity Session</span>
                <span class="pill">⚖️ 25 Legal Judgments</span>
            </div>
        </div>
"""

    for idx, turn in enumerate(turns, 1):
        u_raw = turn["user"]
        a_raw = turn["assistant"]
        if not u_raw and not a_raw:
            continue
            
        u_escaped = html.escape(u_raw)
        
        # We will embed markdown into a script tag or let marked parse it in-browser
        html_content += f"""
        <div class="turn-card" id="turn-{idx}">
            <div class="turn-header">
                <span class="turn-title">💬 Conversation Turn #{idx}</span>
            </div>
            <div class="user-section">
                <div class="user-label">👤 User Request:</div>
                <div class="user-text">{u_escaped}</div>
            </div>
            <div class="assistant-section">
                <div class="assistant-label">🤖 Antigravity Assistant Response:</div>
                <div class="markdown-body" id="md-content-{idx}"></div>
                <textarea id="raw-md-{idx}" style="display:none;">{html.escape(a_raw)}</textarea>
            </div>
        </div>
        """

    html_content += """
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const textareas = document.querySelectorAll('textarea[id^="raw-md-"]');
            textareas.forEach(ta => {
                const id = ta.id.replace('raw-md-', '');
                const target = document.getElementById('md-content-' + id);
                if (target && ta.value) {
                    target.innerHTML = marked.parse(ta.value);
                }
            });
            hljs.highlightAll();
        });
    </script>
</body>
</html>
"""

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML exported to: {html_file}")

if __name__ == "__main__":
    export_conversation()
