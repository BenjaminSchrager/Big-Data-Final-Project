from pathlib import Path
import sys
import pdfplumber



SECTION_KEYWORDS = [
    "education",
    "experience",
    "work experience",
    "relevant experience",
    "employment history",
    "skills",
    "technical skills",
    "projects",
]


def extract_pdf_text(pdf_path: str) -> str:
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    all_text = []

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                all_text.append(page_text)

    return "\n".join(all_text).strip()


def print_section_check(text: str) -> None:
    text_lower = text.lower()

    print("\nSection keywords")
    for keyword in SECTION_KEYWORDS:
        print(f"- {keyword}: {keyword in text_lower}")


def check_pdf_text(pdf_path: str) -> None:
    text = extract_pdf_text(pdf_path)

    print(f"PDF: {pdf_path}")
    print(f"Text length: {len(text)}")

    if len(text) == 0:
        print("\nResult: no readable text found")
        print("This file is likely image-based, scanned, or difficult for pdfplumber to parse.")
        return

    print("\nResult: readable text found")
    print("\nPreview")
    print(text[:2000])

    print_section_check(text)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python pdf_text_check.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    check_pdf_text(pdf_path)


if __name__ == "__main__":
    main()