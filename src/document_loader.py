"""
Document loader module for Indian Legal Judgment corpus.
Extracts digital text from judgment PDFs, matches metadata from Excel,
assigns deterministic IDs D01-D25, and computes descriptive corpus statistics.
"""
from pathlib import Path
import re
import pandas as pd
import pypdf
from typing import Dict, List, Any, Optional, Tuple
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

try:
    from config import (
        get_dataset_dir, get_metadata_file, DOCUMENT_STATISTICS_CSV
    )
except ImportError:
    from ..config import (
        get_dataset_dir, get_metadata_file, DOCUMENT_STATISTICS_CSV
    )

class DocumentLoader:
    """Loads legal PDF documents and binds them with authoritative Excel metadata."""

    def __init__(self, dataset_dir: Optional[str] = None, metadata_path: Optional[str] = None):
        self.dataset_dir = Path(get_dataset_dir(dataset_dir))
        self.metadata_path = Path(get_metadata_file(metadata_path))
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.metadata_df: Optional[pd.DataFrame] = None
        self._load_metadata()

    def _load_metadata(self):
        """Parse Excel metadata and normalize columns."""
        if not self.metadata_path.is_file():
            print(f"Warning: Metadata file not found at {self.metadata_path}")
            return

        try:
            raw_df = pd.read_excel(self.metadata_path, header=None)
            header_row_idx = None
            for idx, row in raw_df.iterrows():
                vals = [str(x).strip() for x in row.values if pd.notna(x)]
                if 'File' in vals and 'Case' in vals:
                    header_row_idx = idx
                    break

            if header_row_idx is not None:
                df = pd.read_excel(self.metadata_path, skiprows=header_row_idx)
                df = df.dropna(how='all', axis=1)
                df.columns = [str(c).strip() for c in df.columns]
                # Ensure filename matching is case-insensitive
                df['File_Key'] = df['File'].str.strip().str.upper()
                self.metadata_df = df
            else:
                print(f"Warning: Could not locate table header in {self.metadata_path}")
        except Exception as e:
            print(f"Error reading metadata Excel: {e}")

    def clean_text_conservative(self, text: str) -> str:
        """
        Conservative text cleaning for legal judgments:
        - Normalizes line breaks and trailing spaces
        - Fixes hyphenated line-breaks without destroying statutory dashes (e.g. 'sub-\nsection' -> 'sub-section')
        - Removes control characters and form-feed bytes
        - Preserves legal punctuation, section symbols, currency, and quotation marks
        """
        if not text:
            return ""
        # Remove null bytes and non-printable control chars except tabs/newlines
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
        # Normalize carriage returns
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Fix soft hyphens at line wraps (e.g., 'juris-\ndiction' -> 'jurisdiction')
        text = re.sub(r'(\b[a-zA-Z]+)-\n([a-zA-Z]+\b)', r'\1\2', text)
        # Normalize multiple spaces per line but keep paragraphs
        lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]
        cleaned_text = '\n'.join(lines)
        # Collapse 3+ newlines to 2
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        return cleaned_text.strip()

    def load_documents(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all PDF documents, link with metadata, assign IDs D01-D25 deterministically,
        and calculate extraction and lexical metrics.
        """
        pdf_files = list(self.dataset_dir.glob("*.PDF")) + list(self.dataset_dir.glob("*.pdf"))
        # Deduplicate paths
        unique_files = {f.name.upper(): f for f in pdf_files}
        
        # If metadata is available, order documents by metadata row number to maintain stable D01-D25
        ordered_files = []
        if self.metadata_df is not None:
            for _, row in self.metadata_df.iterrows():
                f_key = str(row['File_Key'])
                if f_key in unique_files:
                    ordered_files.append((unique_files[f_key], row.to_dict()))
            # Append any PDF files not in metadata alphabetically
            for f_key, f_path in sorted(unique_files.items()):
                if not any(f_path == item[0] for item in ordered_files):
                    ordered_files.append((f_path, None))
        else:
            ordered_files = [(f, None) for f in sorted(unique_files.values(), key=lambda p: p.name)]

        self.documents = {}
        for idx, (file_path, meta) in enumerate(ordered_files, start=1):
            doc_id = f"D{idx:02d}"
            file_name = file_path.name
            
            raw_text = ""
            page_count = 0
            extraction_status = "SUCCESS"
            error_message = ""

            try:
                reader = pypdf.PdfReader(str(file_path))
                page_count = len(reader.pages)
                pages_text = []
                for p_idx, page in enumerate(reader.pages):
                    t = page.extract_text()
                    if t:
                        pages_text.append(t)
                raw_text = "\n\n".join(pages_text)
                if not raw_text.strip():
                    extraction_status = "EMPTY_TEXT"
            except Exception as e:
                extraction_status = "FAILED"
                error_message = str(e)

            cleaned_text = self.clean_text_conservative(raw_text)

            # Compute lexical stats
            try:
                sentences = sent_tokenize(cleaned_text) if cleaned_text else []
                tokens = word_tokenize(cleaned_text) if cleaned_text else []
            except Exception:
                sentences = [s.strip() for s in cleaned_text.split('.') if s.strip()]
                tokens = cleaned_text.split()

            vocab = set(t.lower() for t in tokens if any(c.isalnum() for c in t))

            case_name = meta.get('Case', file_name) if meta else file_name
            court_year = meta.get('Court / Year', 'Unknown') if meta else 'Unknown'
            sector = meta.get('Sector', 'General Legal') if meta else 'General Legal'
            key_law = meta.get('Key law', 'N/A') if meta else 'N/A'

            self.documents[doc_id] = {
                "document_id": doc_id,
                "file_name": file_name,
                "file_path": str(file_path),
                "case_name": case_name,
                "court_year": court_year,
                "sector": sector,
                "key_law": key_law,
                "pages": page_count,
                "raw_text": raw_text,
                "cleaned_text": cleaned_text,
                "char_count": len(cleaned_text),
                "sentence_count": len(sentences),
                "token_count": len(tokens),
                "vocab_size": len(vocab),
                "extraction_status": extraction_status,
                "error_message": error_message
            }

        return self.documents

    def generate_statistics_df(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Generate detailed document statistics table and summary dictionary.
        Returns (per_doc_df, summary_metrics).
        """
        if not self.documents:
            self.load_documents()

        rows = []
        for doc_id, doc in self.documents.items():
            rows.append({
                "Document ID": doc["document_id"],
                "File Name": doc["file_name"],
                "Case Name": doc["case_name"],
                "Court / Year": doc["court_year"],
                "Sector": doc["sector"],
                "Key Law": doc["key_law"],
                "Pages": doc["pages"],
                "Characters": doc["char_count"],
                "Sentences": doc["sentence_count"],
                "Tokens": doc["token_count"],
                "Vocabulary Size": doc["vocab_size"],
                "Extraction Status": doc["extraction_status"]
            })

        df = pd.DataFrame(rows)

        total_docs = len(df)
        total_sentences = df["Sentences"].sum()
        total_tokens = df["Tokens"].sum()
        total_chars = df["Characters"].sum()
        avg_doc_length = round(total_tokens / total_docs, 2) if total_docs > 0 else 0

        # Corpus-wide unique vocabulary
        all_tokens = []
        for doc in self.documents.values():
            text = doc["cleaned_text"]
            try:
                toks = word_tokenize(text)
            except Exception:
                toks = text.split()
            all_tokens.extend([t.lower() for t in toks if any(c.isalnum() for c in t)])
        corpus_vocab_size = len(set(all_tokens))

        summary = {
            "Number of documents": total_docs,
            "Number of sentences": int(total_sentences),
            "Number of tokens": int(total_tokens),
            "Number of characters": int(total_chars),
            "Vocabulary size": corpus_vocab_size,
            "Average document length": avg_doc_length,
            "Counting conventions": (
                "Documents: Total extracted legal judgment files. "
                "Sentences: NLTK sent_tokenize on conservatively cleaned judgment text. "
                "Tokens: NLTK word_tokenize output. "
                "Characters: Total string length of cleaned text. "
                "Vocabulary size: Distinct lowercased alphanumeric tokens across full corpus. "
                "Average document length: Total tokens divided by total documents."
            )
        }

        return df, summary

    def export_statistics_csv(self, output_path: Optional[Path] = None) -> Path:
        """Export document statistics table to CSV."""
        df, _ = self.generate_statistics_df()
        out = output_path or DOCUMENT_STATISTICS_CSV
        df.to_csv(out, index=False, encoding='utf-8')
        return out
