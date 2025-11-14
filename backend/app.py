import asyncio
from pathlib import Path
from typing import List, Dict, Union, Optional
import pandas as pd

from src.file_reader import read_text_file, read_csv_file, read_pdf_file, read_doc_file
from src.associational_algorithm import AssociationalOntologyCreator
from src.generate_knowledge_graph import visualize_graph


async def generate_knowledge_graph_html(
    files: Optional[List[Dict[str, Union[str, bytes]]]] = None,
    raw_text: Optional[str] = None
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
    # result = {
    #     'html': None,
    #     'graph_data': None,
    #     'error': None,
    #     'processed_text': None
    # }
    
    # Step 1: Read and process document content
    full_text = []
    
    if raw_text:
        full_text.append({"name": "raw_text", "content": raw_text})
    
    if files:
        for file_dict in files:
            file_name = file_dict.get('name', 'unknown')
            file_content = file_dict.get('content')
            file_extension = file_dict.get('extension', Path(file_name).suffix).lower()
            
            try:
                if file_extension == ".txt":
                    text_content = read_text_file(file_content)
                    full_text.append({"name": file_name, "content": text_content})
                    
                elif file_extension == ".csv":
                    df = read_csv_file(file_content)
                    if df is not None:
                        full_text.append({"name": file_name, "content": df})
                        
                elif file_extension == ".pdf":
                    pdf_content = read_pdf_file(file_content)
                    full_text.append({"name": file_name, "content": pdf_content})
                    
                elif file_extension == ".docx":
                    doc_content = read_doc_file(file_content)
                    full_text.append({"name": file_name, "content": doc_content})
                    
                else:
                    # result['error'] = f"Unsupported file type: {file_name}"
                    # return result
                    return None
                    
            except Exception as e:
                # result['error'] = f"Error reading file {file_name}: {str(e)}"
                # return result
                return None
    
    # Check if we have any content to process
    if not full_text:
        # result['error'] = "No content provided. Please provide files or raw text."
        # return result
        return None
    
    # Step 2: Generate the knowledge graph
    try:
        creator = AssociationalOntologyCreator(llm_name="", api_key="") #this is where we would pass in the AI connection info
        graph_document = await creator.create_associational_ontology(full_text)
        
        # Validate graph document
        if graph_document and graph_document.nodes:
            html_output = visualize_graph(graph_document)
            return html_output
        else:
            # result['error'] = "Graph generation failed: No valid nodes or relationships were extracted from the text."
            return None

            
    except Exception as e:
        # result['error'] = f"An error occurred during graph generation: {str(e)}"
        return None
    
    # return result['html']


def generate_knowledge_graph_html_sync(
    files: Optional[List[Dict[str, Union[str, bytes]]]] = None,
    raw_text: Optional[str] = None
) -> Optional[str]:
    """
    Synchronous wrapper for generate_knowledge_graph_html.
    
    Args:
        files: List of file dictionaries (see async version for details)
        raw_text: Optional raw text string to process
    
    Returns:
        HTML string (or None if error)
    """
    return asyncio.run(generate_knowledge_graph_html(files, raw_text))


# Example usage:
if __name__ == "__main__":
    # Example 1: Process raw text
    html = generate_knowledge_graph_html_sync(raw_text="Your text content here")
    
    if html:
        print("HTML generated successfully!")
        # Save to file
        with open("knowledge_graph.html", "w", encoding="utf-8") as f:
            f.write(html)
    else:
        print("Error: Failed to generate HTML")
    
    # Example 2: Process files
    # files = [
    #     {
    #         'name': 'document.txt',
    #         'content': open('document.txt', 'rb'),
    #         'extension': '.txt'
    #     },
    #     {
    #         'name': 'data.pdf',
    #         'content': open('data.pdf', 'rb'),
    #         'extension': '.pdf'
    #     }
    # ]
    # html = generate_knowledge_graph_html_sync(files=files)

