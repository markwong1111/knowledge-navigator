import pandas as pd
import io
import warnings

# Use pypdf as it is more robust for RAG/Graph applications
# Ensure 'pypdf' is in your requirements.txt
try:
    from pypdf import PdfReader
    pypdf_available = True
except ImportError:
    pypdf_available = False
    print("Warning: 'pypdf' library not found. PDF reading will fail.")

# --- For .doc/.docx files ---
try:
    import docx
except ImportError:
    docx = None
    print("Warning: 'python-docx' library not found. DOCX reading will fail.")


def read_text_file(file_obj) -> str:
    """Reads content from a plain text file."""
    try:
        # Reset cursor to start
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
            
        # Read bytes
        content_bytes = file_obj.read()
        
        # Decode
        return content_bytes.decode('utf-8')
    except Exception as e:
        print(f"Error reading text file: {e}")
        return ""


def read_csv_file(file_obj) -> pd.DataFrame | None:
    """Reads content from a CSV file."""
    try:
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
            
        # pandas can read directly from BytesIO
        df = pd.read_csv(file_obj)
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None


def read_pdf_file(file_obj) -> str:
    """
    Reads content from a PDF file using pypdf.
    """
    if not pypdf_available:
        print("Error: 'pypdf' is not installed.")
        return ""
        
    try:
        # Reset cursor to start is CRITICAL for pypdf
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
            
        reader = PdfReader(file_obj)
        text = ""
        
        # Iterate over pages
        for i, page in enumerate(reader.pages):
            content = page.extract_text()
            if content:
                text += content + "\n"
        
        print(f"Successfully extracted {len(text)} characters from PDF")
        return text
        
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        # Helpful for debugging in deployment logs
        import traceback
        traceback.print_exc()
        return ""


def read_doc_file(file_obj) -> str:
    """Reads content from a .docx file."""
    if not docx:
        print("Error: 'python-docx' is not installed.")
        return ""
        
    try:
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
            
        document = docx.Document(file_obj)
        full_text = []
        for para in document.paragraphs:
            full_text.append(para.text)
            
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error reading DOCX file: {e}")
        return ""
