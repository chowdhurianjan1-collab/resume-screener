"""
pdf_extractor.py — turns an uploaded resume file into plain text.

Supports PDF (via PyMuPDF/fitz) and DOCX (via python-docx). Also pulls out
an email and phone number with regex so the UI can show contact info
straight from the scanned file.
"""
import io
import re
from typing import Optional, Tuple

import fitz  # PyMuPDF
import docx  # python-docx

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        for page in pdf:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    document = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in document.paragraphs)


def extract_text(filename: str, file_bytes: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    if lower.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    raise ValueError(f"Unsupported file type: {filename}. Use PDF, DOCX, or TXT.")


def guess_candidate_name(text: str, fallback: str) -> str:
    """Best-effort: the first non-empty line that isn't an email/phone/URL
    is usually the candidate's name at the top of a resume."""
    for line in text.splitlines():
        line = line.strip()
        if not line or len(line) > 60:
            continue
        if EMAIL_RE.search(line) or "http" in line.lower():
            continue
        if any(ch.isdigit() for ch in line) and len(line.split()) < 3:
            continue
        return line
    return fallback


def extract_contact_info(text: str) -> Tuple[Optional[str], Optional[str]]:
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    email = email_match.group(0) if email_match else None
    phone = phone_match.group(0).strip() if phone_match else None
    return email, phone
