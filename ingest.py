
import fitz  # PyMuPDF
from pathlib import Path

# PDF file location
PDF_PATH = Path("documents/the_last_signal_series_guide.pdf")

def extract_text(pdf_path):

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document = fitz.open(pdf_path)

    extracted_pages = []

    print(f"Total pages: {len(document)}")

    for page_number, page in enumerate(document):

        text = page.get_text("text")

        if text.strip():
            extracted_pages.append({
                "page": page_number + 1,
                "text": text
            })

    document.close()

    print(f"Successfully extracted {len(extracted_pages)} pages.")

    return extracted_pages


if __name__ == "__main__":

    pages = extract_text(PDF_PATH)

    for page in pages[:2]:
        print(f"\n--- Page {page['page']} ---\n")
        print(page["text"][:1000])


# Code	Meaning
# fitz.open()	Opens the PDF
# len(document)	Counts PDF pages
# page.get_text()	Extracts text from a page
# enumerate()	Iterates through pages
# extracted_pages	Stores text and page numbers