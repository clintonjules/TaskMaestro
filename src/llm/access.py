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

from src.utils.ollama_tools import ollama_model_installed

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")

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

        Config keys:
          - llm_type: 'api' or 'local'
          - api_provider: The name of the LLM provider.
          - model: Model identifier string.
          - role_description: (optional) A system prompt for the model.
        """
        self.llm_type = config.get('llm_type')
        self.api_provider = config.get('api_provider')
        self.model = config.get('model')
        self.role_description = config.get('role_description', [])

        if self.llm_type not in ('api', 'local'):
            raise ValueError("config 'type' must be either 'api' or 'local'")
        
        if self.llm_type == 'api' and self.api_provider not in API_LLM_PROVIDERS:
            raise ValueError(f"Unsupported provider: {self.api_provider}")
     
        
    def call(self, prompt: str, **kwargs) -> str:
        """
        Call the underlying LLM with the provided prompt.

        Additional parameters can be passed via kwargs.
        
        Returns:
            The generated response as a string.
        """
        if self.llm_type == 'api':
            if self.api_provider == 'openai':
                return self._call_openai(prompt, **kwargs)
        
            elif self.api_provider == 'anthropic':
                return self._call_anthropic(prompt, **kwargs)
            
            elif self.api_provider == 'google':
                return self._call_google(prompt, **kwargs)
            
            elif self.api_provider == 'deepseek':
                return self._call_deepseek(prompt, **kwargs)
            
            elif self.api_provider == 'xai':
                return self._call_xai(prompt, **kwargs)
            
            else:
                raise ValueError(f"Unsupported provider: {self.api_provider}")
            
        elif self.llm_type == 'local':
            return self._call_local(prompt, **kwargs)
        
        else:
            raise ValueError(f"Unsupported llm_type: {self.llm_type}")


    def _call_openai(self, prompt: str, role_description: str = None, **kwargs) -> str:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        messages = [
                {"role": "developer", "content": role_description},
                {"role": "user", "content": prompt}
            ]
        
        response = client.chat.completions.create(
            model=self.model,
            messages=messages
        )
    
        return response.choices[0].message.content


    def _call_anthropic(self, prompt: str, role_description: str = None, **kwargs) -> str:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        response = client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=role_description,
            messages= [
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    
    def _call_google(self, prompt: str, role_description: str = None, **kwargs) -> str:
        client = genai.Client(api_key=GOOGLE_API_KEY)

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            system_instruction=role_description
        )

        return response.text
    
    
    def _call_deepseek(self, prompt: str, role_description: str = None, **kwargs) -> str:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": role_description},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )

        return response.choices[0].message.content
    
    
    def _call_xai(self, prompt: str, role_description: str = None, **kwargs) -> str:
        client = OpenAI(
            api_key=XAI_API_KEY,
            base_url="https://api.x.ai/v1",
        )

        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": role_description},
                {"role": "user", "content": prompt},
            ],
        )
        
        return completion.choices[0].message.content
    

    def _call_local(self, prompt: str, role_description: str = None, **kwargs) -> str:
        model_installed = ollama_model_installed(self.model)

        if model_installed:
            response: ChatResponse = chat(model=self.model, messages=[
                {"role": "system", "content": role_description},
                {"role": "user", "content": prompt}
            ])
            
            return response.message.content
    
        else:
            raise ValueError(f"Model {self.model} is not installed")