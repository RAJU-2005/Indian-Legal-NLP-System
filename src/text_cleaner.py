"""
Text cleaning and normalization module for Indian Legal Judgments.
Supports both conservative normalization (preserving statutory citations and case numbers)
and standard baseline normalization.
"""
import re
from typing import Dict, Any

class LegalTextCleaner:
    """Provides conservative and aggressive cleaning strategies for legal texts."""

    @staticmethod
    def clean_conservative(text: str) -> str:
        """
        Conservative cleaning:
        - Removes non-printable characters and control bytes.
        - Unifies unicode quotation marks, dashes, and currency symbols (e.g. Rs., ₹).
        - Fixes line wraps without removing hyphens inside statutory or section references.
        - Preserves legal case names, sections, and punctuation.
        """
        if not text:
            return ""
        # Remove non-printable control chars except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
        # Normalize carriage returns
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Normalize unicode quotes
        text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
        # Normalize en-dash and em-dash
        text = text.replace('—', '-').replace('–', '-')
        # Fix soft hyphens across line breaks (e.g., 'sub-\nsection' -> 'sub-section')
        text = re.sub(r'(\b[a-zA-Z]+)-\n([a-zA-Z]+\b)', r'\1-\2', text)
        # Collapse multiple whitespace characters into single space per line
        lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]
        cleaned = '\n'.join(lines)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        return cleaned.strip()

    @staticmethod
    def clean_baseline(text: str) -> str:
        """
        Baseline cleaning:
        - Converts to lowercase.
        - Removes non-alphanumeric characters except basic spaces.
        - Collapses all whitespace.
        """
        if not text:
            return ""
        text = text.lower()
        # Keep alphanumeric and spaces only
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
