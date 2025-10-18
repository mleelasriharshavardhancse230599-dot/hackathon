import fitz  # PyMuPDF
import docx
import io

def extract_text_from_pdf_bytes(b):
    doc = fitz.open(stream=b, filetype="pdf")
    text = []
    for page in doc:
        text.append(page.get_text())
    return "\n".join(text)

def extract_text_from_docx_bytes(b):
    with io.BytesIO(b) as bio:
        doc = docx.Document(bio)
        return "\n".join(p.text for p in doc.paragraphs)

def extract_text(filename, raw_bytes):
    fn = filename.lower()
    try:
        if fn.endswith(".pdf"):
            return extract_text_from_pdf_bytes(raw_bytes)
        elif fn.endswith(".docx"):
            return extract_text_from_docx_bytes(raw_bytes)
        else:
            return raw_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return ""
