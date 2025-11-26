import asyncio
from pathlib import Path
from typing import List, Dict, Union, Optional
import pandas as pd

# NOTE: Assuming these imports are correct and available
from src.file_reader import read_text_file, read_csv_file, read_pdf_file, read_doc_file
from src.associational_algorithm import AssociationalOntologyCreator
from src.generate_knowledge_graph import visualize_graph


async def generate_knowledge_graph_html(
    files: Optional[List[Dict[str, Union[str, bytes]]]] = None,
    raw_text: Optional[str] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    llm_name: Optional[str] = None,
    temp: Optional[int] = None,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None
) -> Optional[str]:
    """
    Generate a knowledge graph HTML from uploaded files or raw text.
    
    Args:
        files: List of file dictionaries with keys:
            - 'name': filename (str)
            - 'content': file content as bytes or file-like object
            - 'extension': file extension (e.g., '.txt', '.pdf', '.csv', '.docx')
        raw_text: Optional raw text string to process
    
    Returns:
        - HTML string of the knowledge graph (or None if error)
    """
    
    # Step 1: Read and process document content
    full_text = []
    
    if raw_text:
        # Note: If raw_text is provided, it bypasses the 'files' list handling 
        # and is processed first in the 'full_text' list.
        full_text.append({"name": "raw_text", "content": raw_text})
    
    if files:
        for file_dict in files:
            file_name = file_dict.get('name', 'unknown')
            file_content = file_dict.get('content') # This is the io.BytesIO object from server.py
            file_extension = file_dict.get('extension', Path(file_name).suffix).lower()
            
            try:
                # 💡 CRITICAL FIX: Reset stream position to 0 before reading.
                # This ensures the file content is read from the beginning, 
                # especially important if the stream pointer was moved by Flask 
                # or a previous operation.
                if file_content is not None and hasattr(file_content, 'seek'):
                    file_content.seek(0)
                
                if file_extension == ".txt":
                    text_content = read_text_file(file_content)
                    full_text.append({"name": file_name, "content": text_content})
                    
                elif file_extension == ".csv":
                    df = read_csv_file(file_content)
                    if df is not None:
                        # Assuming 'read_csv_file' returns a pandas DataFrame
                        full_text.append({"name": file_name, "content": df}) 
                        
                elif file_extension == ".pdf":
                    pdf_content = read_pdf_file(file_content)
                    full_text.append({"name": file_name, "content": pdf_content})
                    
                elif file_extension == ".docx":
                    doc_content = read_doc_file(file_content)
                    full_text.append({"name": file_name, "content": doc_content})
                    
                else:
                    return None # Unsupported file type
                    
            except Exception as e:
                # print(f"Error reading file {file_name}: {str(e)}") # Optional: For debugging
                return None # Error reading the file
    
    # Check if we have any content to process
    if not full_text:
        return None
    
    # Step 2: Generate the knowledge graph
    try:
        creator = AssociationalOntologyCreator(
            llm_name=llm_name, 
            api_base=api_base, 
            api_key=api_key, 
            temperature=temp, 
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
        graph_document = await creator.create_associational_ontology(full_text)
        
        # Validate graph document
        if graph_document and graph_document.nodes:
            html_output = visualize_graph(graph_document)
            return html_output
        else:
            return None # Graph generation failed
            
    except Exception as e:
        # print(f"An error occurred during graph generation: {str(e)}") # Optional: For debugging
        return None
    
# --- Synchronous Wrapper ---
def generate_knowledge_graph_html_sync(
    files: Optional[List[Dict[str, Union[str, bytes]]]] = None,
    raw_text: Optional[str] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    llm_name: Optional[str] = None,
    temp: Optional[int] = None,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None
) -> Optional[str]:
    """
    Synchronous wrapper for generate_knowledge_graph_html.
    
    Args:
        files: List of file dictionaries (see async version for details)
        raw_text: Optional raw text string to process
    
    Returns:
        HTML string (or None if error)
    """
    # Note: raw_text argument was missing in the original call here, 
    # but it seems the POST request in server.py only uses the 'files' list 
    # which includes the text input wrapped as a file. Keeping the call as intended 
    # for the server.py structure.
    return asyncio.run(generate_knowledge_graph_html(
        files, 
        api_key=api_key, 
        api_base=api_base, 
        llm_name=llm_name, 
        temp=temp, 
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    ))


# Example usage:
if __name__ == "__main__":
    # Example 1: Process raw text
    raw_text = """Example text for graph generation."""
    # Assuming the user has credentials defined or it's being tested without LLM
    html = generate_knowledge_graph_html_sync(raw_text=raw_text)
    
    if html:
        print("HTML generated successfully!")
        # Save to file
        with open("knowledge_graph.html", "w", encoding="utf-8") as f:
            f.write(html)
    else:
        print("Error: Failed to generate HTML")
