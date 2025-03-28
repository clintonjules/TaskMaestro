import os
import sys
from typing import Dict
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

# LLM Client Providers
from openai import OpenAI # ChatGPT, DeepSeek, Grok
import anthropic # Claude
from google import genai # Gemini

from ollama import ChatResponse, chat

from src.utils.ollama_model import _ollama_model_installed

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")

# Base URLs
DEEPSEEK_URL = "https://api.deepseek.com"
XAI_URL = "https://api.x.ai/v1"

# LLM Providers
API_LLM_PROVIDERS = [
    "openai",
    "anthropic",
    "google",
    "deepseek",
    "xai"
]

class LLMAccess:
    """
    A unified access layer for different LLM providers.

    This layer provides generic access to LLMs, whether accessed via API or locally.
    The configuration should supply the necessary endpoint URLs and headers.
    """

    def __init__(self, config: Dict):
        """
        Initialize the LLMAccess instance.

        Expected config keys:
          - id: A unique identifier for this LLM instance.
          - type: 'api' or 'local'
          - provider: A generic identifier for the provider.
          - model: Model identifier string.
          - api_key: API key for API-based models (if applicable).
          - api_url: (for API-based LLMs) The endpoint URL.
          - local_url: (for local LLMs) The endpoint URL.
          - headers: (optional) HTTP headers to include in requests.
        """
        self.config = config
        self.id = config.get('id', 'default')
        self.llm_type = config.get('type')
        self.provider = config.get('provider')
        self.model = config.get('model')
        self.api_key = config.get('api_key')
        self.api_url = config.get('api_url')
        self.developer_content = config.get('developer_content', None)
        
        if self.llm_type not in ('api', 'local'):
            raise ValueError("config 'type' must be either 'api' or 'local'")
        
        if self.llm_type == 'api' and self.provider not in API_LLM_PROVIDERS:
            raise ValueError(f"Unsupported provider: {self.provider}")
     
        
    def call(self, prompt: str, **kwargs) -> str:
        """
        Call the underlying LLM with the provided prompt.

        Additional parameters can be passed via kwargs.
        
        Returns:
            The generated response as a string.
        """
        if self.llm_type == 'api':
            if self.provider == 'openai':
                return self._call_openai(prompt, **kwargs)
        
            elif self.provider == 'anthropic':
                return self._call_anthropic(prompt, **kwargs)
            
            elif self.provider == 'google':
                return self._call_google(prompt, **kwargs)
            
            elif self.provider == 'deepseek':
                return self._call_deepseek(prompt, **kwargs)
            
            elif self.provider == 'xai':
                return self._call_xai(prompt, **kwargs)
            
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
        elif self.llm_type == 'local':
            return self._call_local(prompt, **kwargs)
        
        else:
            raise ValueError(f"Unsupported llm_type: {self.llm_type}")


    def _call_openai(self, prompt: str, **kwargs) -> str:
        client = OpenAI(api_key=self.api_key)
        
        if self.developer_content:
            messages = [
                {"role": "developer", "content": self.developer_content},
                {"role": "user", "content": prompt}
            ]
        else:
            messages = [
                {"role": "user", "content": prompt}
            ]
        
        response = client.chat.completions.create(
            model=self.model,
            messages=messages
        )
    
        return response.choices[0].message.content


    def _call_anthropic(self, prompt: str, **kwargs) -> str:
        client = anthropic.Anthropic(api_key=self.api_key)
        
        response = client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self.developer_content if self.developer_content else None,
            messages= [
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    def _call_google(self, prompt: str, **kwargs) -> str:
        pass
    
    def _call_deepseek(self, prompt: str, **kwargs) -> str:
        pass
    
    def _call_xai(self, prompt: str, **kwargs) -> str:
        pass
    

    def _call_local(self, prompt: str, **kwargs) -> str:
        model_installed = _ollama_model_installed(self.model)

        if model_installed:
            if self.developer_content:
                response: ChatResponse = chat(model=self.model, messages=[
                {"role": "system", "content": self.developer_content},
                {"role": "user", "content": prompt}
                ])
                
            else:
                response: ChatResponse = chat(model=self.model, messages=[
                {'role': 'user','content': prompt,},
                ])
            
            return response.message.content
    
        else:
            raise ValueError(f"Model {self.model} is not installed")
        

