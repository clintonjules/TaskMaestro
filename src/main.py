import sys
import argparse
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from agents.router import Router
from agents.manager import ManagerAgent
from agents.worker import WorkerAgent

def main():
    parser = argparse.ArgumentParser(description="Run TaskMaestro with custom LLM config.")
    parser.add_argument("--type", "-t", dest="llm_type", required=True, help="LLM type: 'api' or 'local'")
    parser.add_argument("--provider", "-p", dest="api_provider", required=False, help="LLM provider, e.g., 'openai', 'ollama'")
    parser.add_argument("--model", "-m", required=True, help="LLM model name")

    args = parser.parse_args()
    
    router = Router()
    
    manager_config = {
        "llm_type": args.llm_type,
        "api_provider": args.api_provider,
        "model": args.model
    }
    manager = ManagerAgent(manager_config)

    manager_output = manager.plan_task("How to bake a cake")
    router.execute_manager_output(manager_output)
    
    
    
if __name__ == "__main__":
    main()
    
# python src/main.py -t api -p openai -m gpt-4o-mini