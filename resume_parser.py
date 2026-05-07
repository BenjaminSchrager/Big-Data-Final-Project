import re
from pathlib import Path

try:
    import pdfplumber
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "pdfplumber is not installed. Run: python -m pip install pdfplumber"
    )


COMMON_SECTION_HEADERS = [
    "EDUCATION",
    "PROFESSIONAL EXPERIENCE",
    "EXPERIENCE",
    "WORK EXPERIENCE",
    "SKILLS",
    "TECHNICAL SKILLS",
    "PROJECTS",
    "ACTIVITIES",
    "LEADERSHIP",
]


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a text-based PDF resume.
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


def split_resume_sections(text: str) -> dict[str, str]:
    """
    Split resume text into sections using common all-caps section headers.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    sections: dict[str, list[str]] = {"HEADER": []}
    current_section = "HEADER"

    for line in lines:
        if line in COMMON_SECTION_HEADERS:
            current_section = line
            if current_section not in sections:
                sections[current_section] = []
        else:
            sections[current_section].append(line)

    return {section: "\n".join(content).strip() for section, content in sections.items()}


if __name__ == "__main__":
    sample_path = "sample_resume.pdf"
    try:
        extracted = extract_text_from_pdf(sample_path)
        print(extracted[:3000])

        print("\n=== SECTIONS ===")
        sections = split_resume_sections(extracted)
        for name, content in sections.items():
            print(f"\n--- {name} ---")
            print(content[:500])

    except Exception as e:
        print(f"Error: {e}")