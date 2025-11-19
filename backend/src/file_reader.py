import pandas as pd
import csv
import os
from typing import IO
from streamlit.runtime.uploaded_file_manager import UploadedFile
import io
from docx import Document

# --- For .pdf files ---
try:
    from pdfminer.high_level import extract_text
    from pdfminer.layout import LAParams
except ImportError:
    pdfminer = None
    print("Warning: 'pdfminer' library not found. PDF file reading functionality will be limited.")

# --- For .doc/.docx files ---
try:
    import docx
except ImportError:
    docx = None
    print("Warning: 'python-docx' library not found. DOCX file reading functionality will be limited.")
    print("Note: Reading older '.doc' files is more complex and not directly supported by python-docx.")

def read_text_file(uploaded_file: UploadedFile) -> str:
    """
    Reads content from a plain text file (.txt, .rtf) from an UploadedFile object.
    """
    try:
        content = uploaded_file.getvalue().decode('utf-8')
        return content
    except Exception as e:
        print(f"Error reading text file: {e}")
        return ""

def read_csv_file(uploaded_file: UploadedFile) -> pd.DataFrame | None:
    """
    Reads content from a CSV file from an UploadedFile object using pandas.
    """
    try:
        # Use pandas to read the file directly from the uploaded file's buffer
        df = pd.read_csv(io.BytesIO(uploaded_file.getvalue()))
        # print(f"Successfully extracted {len(df)} characters from PDF: {uploaded_file.name}")
        # print(f"PDF Content Preview: {df[:500]}...")
        return df
    except Exception as e:
        print(f"Error reading CSV file with pandas: {e}")
        return None

def read_pdf_file(uploaded_file) -> str:
    """
    Reads content from a PDF file using pdfminer.six.
    
    Args:
        uploaded_file: File object (can be UploadedFile, BytesIO, or file-like object)
    
    Returns:
        str: Extracted text content from the PDF
    """
    if not pdfminer:
        print("Error: 'pdfminer.six' library is not installed. Cannot read PDF files.")
        print("Install with: pip install pdfminer.six")
        return ""
    
    try:
        # Handle different types of file objects
        if hasattr(uploaded_file, 'getvalue'):
            # Streamlit UploadedFile
            pdf_bytes = uploaded_file.getvalue()
        elif hasattr(uploaded_file, 'read'):
            # File-like object (e.g., BytesIO)
            pdf_bytes = uploaded_file.read()
            uploaded_file.seek(0)  # Reset for potential re-reading
        else:
            raise ValueError("Unsupported file object type")
        
        # Use pdfminer.six to extract text
        # LAParams helps with better text extraction and layout analysis
        text = extract_text(
            io.BytesIO(pdf_bytes),
            laparams=LAParams(
                line_margin=0.5,
                word_margin=0.1,
                char_margin=2.0,
                boxes_flow=0.5
            )
        )
        
        print(f"Successfully extracted {len(text)} characters from PDF")
        if text:
            print(f"PDF Content Preview: {text[:500]}...")
        
        return text.strip()
        
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        import traceback
        traceback.print_exc()
        return ""


def read_doc_file(uploaded_file: UploadedFile) -> str:
    """
    Reads content from a .docx file from an UploadedFile object using python-docx.
    """

    print("inside function")
    if not docx:
        print("Error: 'python-docx' library is not installed. Cannot read DOCX files.")
        return ""
        
    try:
        # Use python-docx to read the file directly from the uploaded file's buffer
        document = docx.Document(io.BytesIO(uploaded_file.getvalue()))
        full_text = []
        for para in document.paragraphs:
            full_text.append(para.text)
        text = '\n'.join(full_text)

        # print(f"Successfully extracted {len(text)} characters from PDF: {uploaded_file.name}")
        # print(f"PDF Content Preview: {text[:500]}...")

        return text
    except Exception as e:
        print(f"Error reading DOCX file: {e}")
        return ""