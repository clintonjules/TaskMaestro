import os
import pytest
from taskmaestro.llm.access import LLMAccess

# Example API-based configuration (e.g., OpenAI-compatible)
api_config = {
    "id": "test-api",
    "type": "api",
    "provider": "generic_api",
    "model": "gpt-3.5-turbo",
    "api_key": os.getenv("OPENAI_API_KEY"),
    "api_url": "https://api.openai.com/v1/chat/completions",
    "headers": {"Content-Type": "application/json"}
}

# Example local configuration (e.g., Ollama-compatible)
local_config = {
    "id": "test-local",
    "type": "local",
    "provider": "generic_local",
    "model": "mistral",
    "local_url": "http://localhost:11434/api/chat",
    "headers": {"Content-Type": "application/json"}
}

@pytest.mark.skipif(not api_config["api_key"], reason="OPENAI_API_KEY not set")
def test_api_call():
    llm = LLMAccess(api_config)
    response = llm.call("Say hello.")
    assert isinstance(response, str)
    assert len(response.strip()) > 0

@pytest.mark.skip(reason="Requires local model running on http://localhost:11434")
def test_local_call():
    llm = LLMAccess(local_config)
    response = llm.call("What is modular programming?")
    assert isinstance(response, str)
    assert len(response.strip()) > 0


# config = {
#     "id": "test-openai",
#     "type": "api",
#     "provider": "openai",
#     "model": "gpt-4o",
#     "api_key": OPENAI_API_KEY,
# }

# llm = LLMAccess(config)
# response = llm.call(prompt="What is the capital of France?")
# print(response)