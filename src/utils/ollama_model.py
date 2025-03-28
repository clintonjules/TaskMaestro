import ollama

def _model_input_for_tag(model_name_input: str) -> bool:
    return ":" in model_name_input

def _local_ollama_models(has_tag: bool = False) -> list:
    if has_tag:
        return [model_name.model for model_name in ollama.list().models]
    else:
        return [model_name.model.split(":")[0] for model_name in ollama.list().models]
    
def _ollama_model_installed(model_name_input: str) -> bool:
    return model_name_input in _local_ollama_models(_model_input_for_tag(model_name_input))