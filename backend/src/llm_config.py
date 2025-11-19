# knowledge_graph_project/src/llm_config.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(temperature=0, model_name=None, api_base=None, api_key=None):
    """
    Returns an LLM instance
    """

        # openai_api_base=lm_studio_api_base,
    llm_instance = ChatOpenAI(
            base_url=api_base,
            api_key=api_key,
            model=model_name,
            temperature=temperature
    )

    print(f"Successfully configured ChatOpenAI for LM Studio model: {model_name}")
    return llm_instance