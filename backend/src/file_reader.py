import pandas as pd
import csv
import os
from typing import IO
from streamlit.runtime.uploaded_file_manager import UploadedFile
import io
from docx import Document

# --- For .pdf files ---
try:
    import pypdf
except ImportError:
    pypdf = None
    print("Warning: 'pypdf' library not found. PDF file reading functionality will be limited.")

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

def read_pdf_file(uploaded_file: UploadedFile) -> str:
    """
    Reads content from a PDF file from an UploadedFile object using pypdf.
    """
    if not pypdf:
        print("Error: 'pypdf' library is not installed. Cannot read PDF files.")
        return ""
    
    try:
        # Use pypdf to read the file directly from the uploaded file's buffer
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        # print(f"Successfully extracted {len(text)} characters from PDF: {uploaded_file.name}")
        # print(f"PDF Content Preview: {text[:500]}...")
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
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