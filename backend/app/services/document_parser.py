import os

import fitz  # pymupdf


def extract_text(file_path: str, content_type: str) -> str:
    if content_type == "application/pdf":
        return _extract_pdf(file_path)
    return _extract_text_file(file_path)


def _extract_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n\n".join(text_parts)


def _extract_text_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


SUPPORTED_TYPES = {
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


def is_supported(content_type: str, filename: str) -> bool:
    if content_type in SUPPORTED_TYPES:
        return True
    ext = os.path.splitext(filename)[1].lower()
    return ext in (".pdf", ".txt", ".md", ".text")


def normalize_content_type(content_type: str, filename: str) -> str:
    if content_type in SUPPORTED_TYPES:
        return content_type
    ext = os.path.splitext(filename)[1].lower()
    type_map = {".pdf": "application/pdf", ".txt": "text/plain", ".md": "text/markdown"}
    return type_map.get(ext, "text/plain")
