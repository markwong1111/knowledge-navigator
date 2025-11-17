# knowledge_graph_project/src/llm_config.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(temperature=0, model_name=None, api_base=None, api_key=None):
    """
    Returns an LLM instance
    """
    OPENAI_API_KEY="AIzaSyBDectKJ04QzSIB9MM5LfjganhHGtTz8oM"

    LLM_MODEL_NAME = model_name if model_name else os.getenv("LLM_MODEL_NAME")
    LM_STUDIO_API_BASE = api_base if api_base else os.getenv("LM_STUDIO_API_BASE")
    OPENAI_API_KEY = api_key if api_key else os.getenv("OPENAI_API_KEY")



        # openai_api_base=lm_studio_api_base,
    llm_instance = ChatOpenAI(
            base_url=api_base,
            api_key=api_key,
            model=model_name,
            temperature=temperature
    )

    llm_instance = ChatOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta",
            api_key="AIzaSyBDectKJ04QzSIB9MM5LfjganhHGtTz8oM",
            model="gemini-2.0-flash",
            temperature=temperature
    )

    print(f"Successfully configured ChatOpenAI for LM Studio model: {model_name}")
    return llm_instance