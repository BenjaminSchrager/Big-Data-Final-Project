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
    "CAREER OBJECTIVE": "PROFILE",
    "CONTACT": "HEADER",
}

INLINE_SECTION_HEADERS = [
    "PROFESSIONAL EXPERIENCE",
    "WORK EXPERIENCE",
    "RELEVANT EXPERIENCE",
    "EMPLOYMENT HISTORY",
    "TECHNICAL SKILLS",
    "LEADERSHIP EXPERIENCE",
    "CAREER OBJECTIVE",
    "EDUCATION",
    "EXPERIENCE",
    "SKILLS",
    "PROJECTS",
    "ACTIVITIES",
    "LEADERSHIP",
    "PROFILE",
    "SUMMARY",
    "LANGUAGES",
    "CONTACT",
]


# Text extraction

def extract_text_from_pdf(pdf_path: str) -> str:
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


def isolate_inline_headers(text: str) -> str:
    for header in sorted(INLINE_SECTION_HEADERS, key=len, reverse=True):
        pattern = rf"\s+({re.escape(header)})\s+"
        text = re.sub(pattern, rf"\n\1\n", text, flags=re.IGNORECASE)
    return text


def clean_resume_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\r", "\n", text)
    text = isolate_inline_headers(text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


# Section parsing

def normalize_section_header(line: str) -> str:
    normalized = line.strip().upper()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.rstrip(":")
    return normalized


def get_section_name(line: str) -> str | None:
    normalized = normalize_section_header(line)

    if normalized in SECTION_ALIASES:
        return SECTION_ALIASES[normalized]

    for header, section_name in SECTION_ALIASES.items():
        if normalized.startswith(header):
            return section_name

    return None


def split_resume_sections(text: str) -> dict[str, str]:
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    sections: dict[str, list[str]] = {"HEADER": []}
    current_section = "HEADER"

    for line in lines:
        section_name = get_section_name(line)

        if section_name is not None:
            current_section = section_name
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


# Local test

def main() -> None:
    sample_path = "sample_resume.pdf"

    try:
        text = extract_text_from_pdf(sample_path)

        print("Preview")
        print(text[:2000])

        print("\nSections")
        sections = split_resume_sections(text)
        for name, content in sections.items():
            if name == "FULL_TEXT":
                continue
            print(f"\n{name}")
            print(content[:400])

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()