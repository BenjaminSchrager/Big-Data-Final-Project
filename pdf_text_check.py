from pathlib import Path
import sys

try:
    import pdfplumber
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "pdfplumber is not installed. Run: python -m pip install pdfplumber"
    )


def extract_pdf_text(pdf_path: str) -> str:
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    all_text = []

    with pdfplumber.open(pdf_file) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                all_text.append(page_text)

    return "\n".join(all_text).strip()


def check_pdf_text(pdf_path: str):
    text = extract_pdf_text(pdf_path)

    print(f"PDF: {pdf_path}")
    print(f"Extracted text length: {len(text)}")

    if len(text) == 0:
        print("\nRESULT: No readable/extractable text found.")
        print("This PDF is likely image-based, scanned, or uses a layout that pdfplumber cannot parse well.")
        return

    print("\nRESULT: Readable/extractable text found.")

    print("\n=== FIRST 2000 CHARACTERS ===")
    print(text[:2000])

    section_keywords = [
        "education",
        "experience",
        "work experience",
        "relevant experience",
        "skills",
        "technical skills",
        "projects",
    ]

    print("\n=== SECTION KEYWORD CHECK ===")
    for keyword in section_keywords:
        print(f"{keyword}: {keyword in text.lower()}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_text_check.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    check_pdf_text(pdf_path)