# knowledge_graph_project/src/associational_algorithm.py
import asyncio
import json
import logging
import re
import traceback
from typing import Dict, List, Any, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from json_repair import repair_json
import tiktoken
# from src.stopwords import nltkStopRemoval

# Set up logging for better error visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- LLM Configuration ---
# Import the function to configure the LLM.
from src.llm_config import get_llm

class AssociationalOntologyCreator:
    """
    This class is responsible for creating a knowledge graph from a text chunk.
    It uses a LangChain ChatPromptTemplate to instruct a local LLM to extract
    entities (Nodes) and relationships (Relationships) from the text.
    """

    def __init__(self,
                chunk_size: int = 4000,
                chunk_overlap: int = 200,
                llm_name=None,
                api_base=None,
                api_key=None):
        """
        Initializes the ontology creator with a specific LLM and chunking strategy.

        Args:
            chunk_size (int): The size of the chunks for text splitting.
            chunk_overlap (int): The overlap between chunks.
        """

        self.llm_name = llm_name
        self.api_base = api_base
        self.api_key = api_key
        self.llm = get_llm(temperature=0.0, model_name=self.llm_name, api_base=self.api_base, api_key=self.api_key)
        
        # Use a text splitter that respects token limits
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=self._tiktoken_len
        )

        self.ontology_prompt_template = ChatPromptTemplate.from_messages([
            ("system",
             "You are a sophisticated AI that extracts knowledge from text. "
             "Your task is to identify a short list of node types to help classify important topics within the included documents. "
             "Respond exclusively with a JSON object. "
             "Do not add any additional text, markdown, or explanations."
             "The JSON object must have one key: 'node_types'. "
             "Evaluate the best set of node types based on the topic of the document and the frequency of important concepts."
             "The exact number of node types may vary, but aim for between 5 and 15 types."),
             ("user", "{text_chunk}")
        ])

        self.graph_prompt_template = ChatPromptTemplate.from_messages([
            ("system",
             "You are a sophisticated AI that extracts knowledge from text. "
             "Your task is to identify and extract all nodes and their relationships. "
             "Respond exclusively with a JSON object. "
             "Do not add any additional text, markdown, or explanations."
             "The JSON object must have two keys: 'nodes' and 'relationships'."
             "Each node must have an 'id' and a 'type'."
             "Each relationship must have a 'source' id, a 'target' id, and a 'type'."
             "Node types should be chosen from the following list: {node_types}."
             "Relationships should be verbs or short phrases that describe the connection, like 'WORKS_AT', 'IS_A', 'LOCATED_IN', 'MENTIONS', etc."),
             ("user", "{text_chunk}")
        ])

        self.nodes_prompt_template = ChatPromptTemplate.from_messages([
            ("system",
             "You are a sophisticated AI that extracts knowledge from text. "
             "Your task is to identify a list of nodes from text. "
             "Respond exclusively with a JSON object. "
             "Do not add any additional text, markdown, or explanations."
             "The JSON object must have one key: 'nodes'. "
             "Each node must have an 'id' and a 'type'. "
             "Evaluate the best set of nodes based on the topic of the document and the most frequently appearing concepts."
             "The number of nodes should depend on the length and complexity of the text, but aim to product a node for every 5-20 words."),
             ("user", "{text_chunk}")
        ])

        self.relationships_prompt_template = ChatPromptTemplate.from_messages([
            ("system",
             "You are a sophisticated AI that extracts knowledge from text. "
             "Your task is to identify a list of relationships from text and the following list of nodes: {nodes} "
             "Respond exclusively with a JSON object. "
             "Do not add any additional text, markdown, or explanations."
             "The JSON object must have two keys: 'nodes' and 'relationships'. "
             "Each node must have an 'id' and a 'type'. "
             "Preserve the nodes provided to you and only add the relationships to the JSON object. "
             "Relationships should be verbs or short phrases that describe the connection, like 'WORKS_AT', 'IS_A', 'LOCATED_IN', 'MENTIONS', etc. "
             "Each JSON object should describe a connection or relationship, and it must have a source, a target, and a type field."
             "The number of nodes should depend on the length and complexity of the text, but aim to product a node for every 5-20 words."),
             ("user", "{text_chunk}")
        ])

        # Create an extraction chain to process chunks
        # Option 1: Generate ontology first, then full graph
        self.ontology_extraction_chain = self.ontology_prompt_template | self.llm
        self.graph_extraction_chain = self.graph_prompt_template | self.llm

        # Option 2: Generate nodes first, then relationships
        self.nodes_extraction_chain = self.nodes_prompt_template | self.llm
        self.relationships_extraction_chain = self.relationships_prompt_template | self.llm

    def _tiktoken_len(self, text: str) -> int:
        """
        Calculates the length of text in tokens using tiktoken.
        """
        try:
            tokenizer = tiktoken.get_encoding("cl100k_base")
            tokens = tokenizer.encode(text, disallowed_special=())
            return len(tokens)
        except Exception as e:
            logger.warning(f"Tiktoken error: {e}. Falling back to character count.")
            return len(text)

    async def create_associational_ontology(self, text_entries) -> GraphDocument:
        """
        Orchestrates the creation of the knowledge graph from multiple documents.
        Each entry in text_entries should be a dict with keys:
            - 'name': document name
            - 'content': document text or dataframe
        """
        if not text_entries:
            logger.warning("Input is empty. Cannot create a graph.")
            return GraphDocument(nodes=[], relationships=[], source=None)

        sem = asyncio.Semaphore(10)
    
        # Prepare all documents first
        all_tasks = []
        
        for entry in text_entries:
            name = entry.get("name", "Unnamed Document")
            content = entry.get("content", "")

            # Convert non-string content (e.g. DataFrames) to string
            if not isinstance(content, str):
                try:
                    content = content.to_string()
                except Exception:
                    content = str(content)

            if not content.strip():
                logger.warning(f"Document '{name}' is empty. Skipping.")
                continue

            # Split into chunks
            chunks = self.text_splitter.split_text(content)
            logger.info(f"Document '{name}' split into {len(chunks)} chunks for processing.")

            # Add all chunk tasks for this document to the global task list
            for chunk in chunks:
                all_tasks.append(
                    self.limited_process_chunk_ontology_graphs(sem, chunk, name)
                )
        
        # Process ALL chunks from ALL documents concurrently
        if not all_tasks:
            logger.warning("No chunks to process from any document.")
            return GraphDocument(nodes=[], relationships=[], source=None)
        
        logger.info(f"Processing {len(all_tasks)} total chunks across all documents concurrently.")
        results = await asyncio.gather(*all_tasks)
        valid_results = [res for res in results if res is not None]

        # Merge all documents’ graphs into one
        if not valid_results:
            logger.warning("No valid results were returned from any document.")
            return GraphDocument(nodes=[], relationships=[], source=None)

        return self.merge_graph_documents(valid_results)
    
    async def create_associational_nodes(self, text: str, text_title) -> GraphDocument:
        """
        Orchestrates the creation of the knowledge graph from raw text,
        using the nodes and relationships prompt templates.
        """
        if not text:
            logger.warning("Input text is empty. Cannot create a graph.")
            return GraphDocument(nodes=[], relationships=[], source=None)
            
        chunks = self.text_splitter.split_text(text)

        logger.info(f"Text split into {len(chunks)} chunks for processing.")
        
        sem = asyncio.Semaphore(10)

        # First extract nodes
        node_tasks = [self.limited_process_chunk_nodes_relationships(sem, chunk, text_title) for chunk in chunks]
        node_results = await asyncio.gather(*node_tasks)

        valid_node_results = [res for res in node_results if res is not None]

        if not valid_node_results:
            logger.warning("No valid node results were returned from the LLM. Cannot create graph.")
            return GraphDocument(nodes=[], relationships=[], source=None)

        return self.merge_graph_documents(valid_node_results)
    

        # # Then extract relationships using the extracted nodes
        # relationship_tasks = [self._process_chunk_with_llm_relationships(chunk) for chunk in chunks]
        # relationship_results = await asyncio.gather(*relationship_tasks)

        # valid_relationship_results = [res for res in relationship_results if res is not None]

        # if not valid_relationship_results:
        #     logger.warning("No valid relationship results were returned from the LLM. Cannot create graph.")
        #     return GraphDocument(nodes=[], relationships=[], source=None)

        # combined_results = valid_node_results + valid_relationship_results

        # return self.merge_graph_documents(combined_results)


    async def _process_chunk_with_llm_ontology_graph(self, text_chunk: str, text_title) -> dict | None:
        """
        Processes a single chunk of text with the LLM asynchronously.
        """
        # first remove stop words from chunk

        # text_chunk = nltkStopRemoval(text_chunk)

        try:
            response1 = await self.ontology_extraction_chain.ainvoke({"text_chunk": text_chunk})
            response2 = await self.graph_extraction_chain.ainvoke({"text_chunk": text_chunk, "node_types": response1.content})
            
            return self._parse_llm_response(response2.content, text_title)
        except Exception as e:
            logger.error(f"Error processing chunk: {e}")
            logger.debug(traceback.format_exc())
            return None
        
    async def _process_chunk_with_llm_nodes_relationships(self, text_chunk: str, text_title) -> dict | None:
        """
        Processes a single chunk of text with the nodes LLM asynchronously.
        """
        try:
            response1 = await self.nodes_extraction_chain.ainvoke({"text_chunk": text_chunk})
            response2 = await self.relationships_extraction_chain.ainvoke({"text_chunk": text_chunk, "nodes": response1.content})

            return self._parse_llm_response(response2.content, text_title)
        except Exception as e:
            logger.error(f"Error processing chunk: {e}")
            logger.debug(traceback.format_exc())
            return None

    async def limited_process_chunk_nodes_relationships(self, sem, chunk, text_title):
        async with sem:
            return await self._process_chunk_with_llm_nodes_relationships(chunk, text_title)
        
    async def limited_process_chunk_ontology_graphs(self, sem, chunk, text_title):
        async with sem:
            return await self._process_chunk_with_llm_ontology_graph(chunk, text_title)

    def _parse_llm_response(self, response_text: str, text_title) -> dict | None:
        """
        Parses the LLM's raw string response into a dictionary,
        handling malformed JSON with json-repair.
        """

        parsed_data = None

        try:
            # Use json-repair to fix common LLM JSON errors, like unquoted keys
            repaired_json_str = repair_json(response_text)
            parsed_data = json.loads(repaired_json_str)

            if not isinstance(parsed_data, dict):
                raise ValueError("Parsed JSON is not a dictionary.")
            
            # Basic validation of the parsed data structure
            if "nodes" not in parsed_data or "relationships" not in parsed_data:
                raise ValueError("JSON must contain 'nodes' and 'relationships' keys.")
            
            for node in parsed_data.get("nodes", []):
                node["document"] = text_title
            
            return parsed_data
        except Exception as e:
            logger.error(f"Failed to parse or repair JSON response: {e}")
            print(parsed_data)
            logger.debug(f"Original response: {response_text}")
            return None

    @staticmethod
    def merge_graph_documents(gd_dicts: List[Dict[str, Any]]) -> GraphDocument:
        """
        Merges a list of graph document dictionaries into a single, consolidated GraphDocument.
        This method de-duplicates nodes and merges relationships.
        """
        logger.info(f"Starting merge_graph_documents with {len(gd_dicts)} documents.")
        
        all_nodes = {}
        all_relationships = []

        # Pass 1: Collect all nodes from all documents
        for gd_dict in gd_dicts:
            if not isinstance(gd_dict, dict):
                logger.warning(f"Received non-dictionary item in gd_dicts: {gd_dict}. Skipping.")
                continue

            for node_data in gd_dict.get("nodes", []):
                if "id" in node_data and "type" in node_data:
                    properties = {}
                    if "document" in node_data:
                        properties["document"] = {node_data["document"]}
                    
                    node = Node(
                        id=node_data["id"],
                        type=node_data["type"],
                        properties=properties
                    )
                    if node.id in all_nodes:
                        #all nodes should have a document so no need to protect this
                        all_nodes[node.id].properties["document"].add(node_data["document"])
                    else:
                        all_nodes[node.id] = node
                else:
                    logger.warning(f"Skipping malformed node data: {node_data}")

        # Pass 2: Collect all relationships, now that all nodes are available
        for gd_dict in gd_dicts:
            if not isinstance(gd_dict, dict):
                continue

            for rel_data in gd_dict.get("relationships", []):
                try:
                    source_id = rel_data.get("source")
                    target_id = rel_data.get("target")
                    rel_type = rel_data.get("type")

                    # Explicitly check that source and target nodes exist in our set of all_nodes
                    if source_id in all_nodes and target_id in all_nodes:
                        source_node = all_nodes[source_id]
                        target_node = all_nodes[target_id]
                        
                        # Use a try...except block to gracefully handle Pydantic validation errors
                        try:
                            relationship = Relationship(
                                source=source_node,
                                target=target_node,
                                type=rel_type
                            )
                            all_relationships.append(relationship)
                        except Exception as pydantic_error:
                            logger.warning(f"Failed to create Pydantic Relationship object: {rel_data}. Error: {pydantic_error}")
                            continue
                    else:
                        logger.warning(f"Skipping relationship due to missing node: {rel_data}")
                except Exception as e:
                    logger.error(f"Error processing relationship data: {rel_data}. Error: {e}")
                    continue
        
        logger.info(f"Merged graph contains {len(all_nodes)} nodes and {len(all_relationships)} relationships.")
        # Corrected line to add the 'source' field, which is required by GraphDocument
        source_document = Document(page_content="User provided content", metadata={"type": "user_input"}) #used to track where graph comes from/which document
        return GraphDocument(nodes=list(all_nodes.values()), relationships=all_relationships, source=source_document)


# --- For testing purposes only ---
async def test_associational_algorithm():
    logger.info("--- Running a self-test for AssociationalOntologyCreator ---")
    
    # Check if LLM is available
    try:
        llm = get_llm(model_name="google_gemma-3-12b-it-qat")
        await llm.ainvoke("Test connectivity.")
        logger.info("LLM connectivity test successful.")
    except Exception as e:
        logger.error(f"LLM connectivity test failed: {e}. Please check LM Studio configuration.")
        return

    test_text = """
    Gemini is a family of large language models created by Google AI. 
    Google AI's mission is to advance artificial intelligence. 
    The models are designed to be highly versatile. 
    LangChain is a framework for developing applications with LLMs.
    It was created by Harrison Chase.
    """
    
    creator = AssociationalOntologyCreator(chunk_size=1000, chunk_overlap=0)
    try:
        graph_document = await creator.create_associational_ontology(test_text)
        if graph_document:
            logger.info("\nSuccessfully created graph document from test text.")
            logger.info(f"Nodes: {[node.id for node in graph_document.nodes]}")
            logger.info(f"Relationships: {[(rel.source.id, rel.type, rel.target.id) for rel in graph_document.relationships]}")
        else:
            logger.warning("Failed to create a merged graph document.")
    except Exception as e:
        logger.error(f"\nAn error occurred during test run: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_associational_algorithm())