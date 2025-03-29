import os
import sys
from typing import Dict
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.utils.ollama_tools import list_ollama_models

from openai import OpenAI
from anthropic import Anthropic
from google import genai

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")
       

def get_model_ids(client: OpenAI | Anthropic ) -> list[str]:
    return [model.id for model in client.models.list().data]

def get_available_api_providers() -> list[str]:
    available = {}
    
    if os.getenv("OPENAI_API_KEY"):
        available["openai"] = get_model_ids(OpenAI())   
         
    if os.getenv("ANTHROPIC_API_KEY"):
        available["claude"] = get_model_ids(Anthropic())
        
    if os.getenv("DEEPSEEK_API_KEY"):
            available["deepseek"] = get_model_ids(OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com"))
        
    if os.getenv("XAI_API_KEY"):
        available["xai"] = get_model_ids(OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai"))
        
    if os.getenv("GOOGLE_API_KEY"):
        available["google"] = [model.display_name for model in genai.Client().models.list()]

    return available

def get_available_local_models() -> list[str]:
    return list_ollama_models()