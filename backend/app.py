import asyncio
from pathlib import Path
from typing import List, Dict, Union, Optional
import pandas as pd
import traceback # Import traceback to print full errors

# Import your modules
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
    
    print("--- 🔍 DEBUG: Starting generate_knowledge_graph_html ---")
    
    full_text = []
    
    # 1. Handle Raw Text
    if raw_text:
        full_text.append({"name": "raw_text", "content": raw_text})
    
    # 2. Handle Files
    if files:
        for file_dict in files:
            file_name = file_dict.get('name', 'unknown')
            file_content = file_dict.get('content') 
            file_extension = file_dict.get('extension', Path(file_name).suffix).lower()
            
            print(f"--- 🔍 DEBUG: Processing file: {file_name} ({file_extension}) ---")

            try:
                # Reset stream position
                if file_content is not None and hasattr(file_content, 'seek'):
                    file_content.seek(0)
                
                content = None
                
                if file_extension == ".txt":
                    content = read_text_file(file_content)
                elif file_extension == ".csv":
                    content = read_csv_file(file_content)
                elif file_extension == ".pdf":
                    # This calls your new src/file_reader.py
                    content = read_pdf_file(file_content)
                elif file_extension == ".docx":
                    content = read_doc_file(file_content)
                else:
                    print(f"Skipping unsupported file type: {file_extension}")
                    continue

                # Check if content extraction actually worked
                if content is not None and len(str(content)) > 0:
                    full_text.append({"name": file_name, "content": content})
                    print(f"--- 🔍 DEBUG: Successfully read {len(str(content))} chars from {file_name}")
                else:
                    print(f"--- 🔍 DEBUG: Warning - Extracted empty content from {file_name}")

            except Exception as e:
                # 🛑 THIS WAS THE PROBLEM BEFORE: It was returning None and stopping everything.
                print(f"!!! CRITICAL ERROR reading file {file_name}: {e}")
                traceback.print_exc()
                # We continue to the next file instead of crashing
                continue 
    
    # 3. Validation
    if not full_text:
        print("--- 🔍 DEBUG: No text extracted from any source. Returning None.")
        return None
    
    # 4. Generate Graph
    try:
        print("--- 🔍 DEBUG: Initializing Ontology Creator ---")
        creator = AssociationalOntologyCreator(
            llm_name=llm_name, 
            api_base=api_base, 
            api_key=api_key, 
            temperature=temp, 
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
        
        print("--- 🔍 DEBUG: Running create_associational_ontology (This calls the LLM) ---")
        graph_document = await creator.create_associational_ontology(full_text)
        
        if graph_document and graph_document.nodes:
            print(f"--- 🔍 DEBUG: Graph generated with {len(graph_document.nodes)} nodes. Visualizing... ---")
            html_output = visualize_graph(graph_document)
            return html_output
        else:
            print("--- 🔍 DEBUG: Graph document was empty or had no nodes. ---")
            return None 
            
    except Exception as e:
        print(f"!!! CRITICAL ERROR during graph generation: {e}")
        traceback.print_exc()
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
    return asyncio.run(generate_knowledge_graph_html(
        files, 
        raw_text=raw_text, # Passed raw_text correctly
        api_key=api_key, 
        api_base=api_base, 
        llm_name=llm_name, 
        temp=temp, 
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    ))
