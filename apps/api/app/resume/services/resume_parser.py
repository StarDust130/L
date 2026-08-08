import zipfile
from io import BytesIO
from pathlib import Path

from app.resume.resume_schema import ExtractedResume
from docx import Document
from fastapi import HTTPException, UploadFile
from pypdf import PdfReader

MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}


def normalize_text(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    clean_lines = [line.strip() for line in lines if line.strip()]

    return "\n".join(clean_lines)


def validate_file(
    filename: str,
    file_bytes: bytes,
) -> str:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX, and TXT files are allowed.",
        )

    if len(file_bytes) > MAX_RESUME_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Resume must be smaller than 5 MB.",
        )

    if extension == ".pdf" and not file_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="This does not look like a valid PDF file.",
        )

    if extension == ".docx":
        is_zip = zipfile.is_zipfile(BytesIO(file_bytes))

        if not is_zip:
            raise HTTPException(
                status_code=400,
                detail="This does not look like a valid DOCX file.",
            )

    return extension


def parse_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))

    pages = [page.extract_text() or "" for page in reader.pages]

    return normalize_text("\n".join(pages))


def parse_docx(file_bytes: bytes) -> str:
    document = Document(BytesIO(file_bytes))
    parts: list[str] = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            parts.append(paragraph.text)

    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]

            if cells:
                parts.append(" | ".join(cells))

    return normalize_text("\n".join(parts))


def parse_txt(file_bytes: bytes) -> str:
    try:
        return normalize_text(
            file_bytes.decode("utf-8-sig"),
        )
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=400,
            detail="TXT file must use UTF-8 encoding.",
        ) from error


async def extract_resume_text(
    file: UploadFile,
) -> ExtractedResume:
    filename = file.filename or ""
    file_bytes = await file.read()

    extension = validate_file(
        filename=filename,
        file_bytes=file_bytes,
    )

    if extension == ".pdf":
        text = parse_pdf(file_bytes)
        file_type = "pdf"

    elif extension == ".docx":
        text = parse_docx(file_bytes)
        file_type = "docx"

    else:
        text = parse_txt(file_bytes)
        file_type = "txt"

    if not text:
        raise HTTPException(
            status_code=422,
            detail=("No text could be extracted. This may be a scanned PDF."),
        )

    return ExtractedResume(
        filename=filename,
        file_type=file_type,
        text=text,
        character_count=len(text),
    )
