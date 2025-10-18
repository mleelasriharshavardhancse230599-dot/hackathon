# helpers.py

import fitz  # PyMuPDF
from io import BytesIO
from docx import Document

def extract_text(filename, file_bytes):
    """
    Extract text from PDF, DOCX, or TXT resumes.
    
    Args:
        filename (str): Name of the file (used to detect file type)
        file_bytes (bytes): File content as bytes
    Returns:
        str: Extracted text
    """
    text = ""
    filename_lower = filename.lower()

    try:
        if filename_lower.endswith(".pdf"):
            # Load PDF from bytes
            pdf = fitz.open(stream=file_bytes, filetype="pdf")
            for page in pdf:
                text += page.get_text()
            pdf.close()

        elif filename_lower.endswith(".docx"):
            # Load DOCX from bytes
            doc = Document(BytesIO(file_bytes))
            for para in doc.paragraphs:
                text += para.text + "\n"

        elif filename_lower.endswith(".txt"):
            text = file_bytes.decode('utf-8', errors='ignore')

        else:
            text = ""
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        text = ""

    return text
