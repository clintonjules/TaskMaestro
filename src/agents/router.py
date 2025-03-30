import json
import ast
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.agents.worker import WorkerAgent
# from agents.manager import ManagerAgent  # Uncomment if needed later

class Router:
    def __init__(self):
        self.results = []

    def execute_manager_output(self, manager_output: str):
        payload = ast.literal_eval(manager_output)

        try:
            agents = payload["agents"]
        except Exception as e:
            raise ValueError(f"Error parsing manager output: {e}")
        
        for agent_spec in agents:
            llm_type = agent_spec.get("llm_type")
            model = agent_spec.get("model")
            task = agent_spec["task"]
            
            if "api_provider" in agent_spec:
                provider = agent_spec.get("api_provider")
                
            config = {
                "llm_type": llm_type,
                "api_provider": provider,
                "model": model
            } if provider else {
                "llm_type": llm_type,
                "model": model
            }

            worker = WorkerAgent(config)

            print(worker.handle_task(task))
            print("-"*100)