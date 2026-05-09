import re
from pathlib import Path

try:
    import pdfplumber
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "pdfplumber is not installed. Run: python -m pip install pdfplumber"
    )


SECTION_ALIASES = {
    "EDUCATION": "EDUCATION",

    "PROFESSIONAL EXPERIENCE": "EXPERIENCE",
    "WORK EXPERIENCE": "EXPERIENCE",
    "EXPERIENCE": "EXPERIENCE",
    "RELEVANT EXPERIENCE": "EXPERIENCE",
    "EMPLOYMENT HISTORY": "EXPERIENCE",

    "SKILLS": "SKILLS",
    "TECHNICAL SKILLS": "SKILLS",
    "HARD SKILLS": "SKILLS",
    "SOFT SKILLS": "SKILLS",

    "PROJECTS": "PROJECTS",
    "ACTIVITIES": "ACTIVITIES",
    "LEADERSHIP": "LEADERSHIP",
    "LEADERSHIP EXPERIENCE": "LEADERSHIP",
    "PROFILE": "PROFILE",
    "SUMMARY": "PROFILE",
    "LANGUAGES": "LANGUAGES",
}


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a text-based PDF resume.
    Returns raw text as a string.
    """
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    all_text = []

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                all_text.append(page_text)

    text = "\n".join(all_text)
    return clean_resume_text(text)


def clean_resume_text(text: str) -> str:
    """
    Clean extracted resume text by normalizing whitespace.
    """
    text = text.replace("\xa0", " ")
    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def normalize_section_header(line: str) -> str:
    """
    Normalize a candidate section header so matching is case-insensitive
    and whitespace/punctuation noise is reduced.
    """
    normalized = line.strip().upper()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.rstrip(":")
    return normalized


def split_resume_sections(text: str) -> dict[str, str]:
    """
    Split resume text into normalized sections using common section aliases.

    Example:
    - 'Education' -> 'EDUCATION'
    - 'Employment History' -> 'EXPERIENCE'
    - 'Technical Skills' -> 'SKILLS'
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    sections: dict[str, list[str]] = {"HEADER": []}
    current_section = "HEADER"

    for line in lines:
        normalized = normalize_section_header(line)

        if normalized in SECTION_ALIASES:
            current_section = SECTION_ALIASES[normalized]
            if current_section not in sections:
                sections[current_section] = []
        else:
            sections[current_section].append(line)

    result = {
        section: "\n".join(content).strip()
        for section, content in sections.items()
    }
    result["FULL_TEXT"] = text
    return result


if __name__ == "__main__":
    sample_path = "sample_resume.pdf"

    try:
        extracted = extract_text_from_pdf(sample_path)
        print("=== FIRST 2000 CHARACTERS ===")
        print(extracted[:2000])

        print("\n=== DETECTED SECTIONS ===")
        sections = split_resume_sections(extracted)
        for name, content in sections.items():
            if name == "FULL_TEXT":
                continue
            print(f"\n--- {name} ---")
            print(content[:500])

    except Exception as e:
        print(f"Error: {e}")