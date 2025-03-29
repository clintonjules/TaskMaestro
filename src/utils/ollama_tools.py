import ollama

def model_input_for_tag(model_name_input: str) -> bool:
    return ":" in model_name_input

def list_ollama_models() -> list:
    return [model_name.model for model_name in ollama.list().models]

def list_ollama_models_without_tags() -> list:
    return [model_name.model.split(":")[0] for model_name in ollama.list().models]

def local_ollama_models(has_tag: bool = False) -> list:
    if has_tag:
        return list_ollama_models()
    else:
        return list_ollama_models_without_tags()
    
def ollama_model_installed(model_name_input: str) -> bool:
    return model_name_input in local_ollama_models(model_input_for_tag(model_name_input))