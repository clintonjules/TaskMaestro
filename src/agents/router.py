import json
import ast
import sys
from pathlib import Path
import uuid
import logging

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.agents.worker import WorkerAgent
# from agents.manager import ManagerAgent  # Uncomment if needed later

class Router:
    def __init__(self):
        self.results = {}
        self.task_dependencies = {}
        self.agent_tasks = {}  # Track tasks by agent
        self.task_to_agent = {}  # Map task IDs to their agent IDs
        self.logger = logging.getLogger(__name__)
        self.logger.info("\n=== Router Initialized ===")

    def _normalize_task_id(self, task_id: str, agent_id: str = None) -> str:
        """
        Normalize a task ID to the format agent_id_task_id.
        If the task_id already contains an agent_id, return it as is.
        """
        if '_' in task_id:
            return task_id
        if agent_id is None:
            agent_id = f"worker-{uuid.uuid4().hex[:8]}"
        normalized_id = f"{agent_id}_{task_id}"
        self.logger.info(f"  Normalized task ID: {task_id} -> {normalized_id}")
        return normalized_id

    def execute_manager_output(self, manager_output: str):
        self.logger.info("\n=== Starting Task Execution ===")
        self.logger.info(f"Received manager output: {manager_output}")
        
        payload = ast.literal_eval(manager_output)

        try:
            agents = payload["agents"]
            self.logger.info(f"\nFound {len(agents)} tasks to execute")
        except Exception as e:
            error_msg = f"Error parsing manager output: {e}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # First pass: collect all tasks and their dependencies
        self.logger.info("\n=== Planning Task Dependencies ===")
        for agent_spec in agents:
            agent_id = agent_spec.get("agent_id", f"worker-{uuid.uuid4().hex[:8]}")
            task_id = agent_spec.get("task_id", str(uuid.uuid4().hex[:8]))
            full_task_id = self._normalize_task_id(task_id, agent_id)
            
            # Store the mapping of task_id to agent_id
            self.task_to_agent[task_id] = agent_id
            
            depends_on = agent_spec.get("depends_on", [])
            # Normalize all dependency task IDs using the correct agent IDs
            depends_on = [self._normalize_task_id(dep, self.task_to_agent.get(dep)) for dep in depends_on]
            
            task_info = f"\nTask: {full_task_id}\n  Agent: {agent_id}\n  Dependencies: {depends_on}\n  Task description: {agent_spec['task']}"
            self.logger.info(task_info)
            
            self.task_dependencies[full_task_id] = {
                "spec": agent_spec,
                "depends_on": depends_on,
                "completed": False,
                "agent_id": agent_id
            }
            
            # Track tasks by agent
            if agent_id not in self.agent_tasks:
                self.agent_tasks[agent_id] = []
            self.agent_tasks[agent_id].append(full_task_id)

        # Validate dependencies before execution
        self.logger.info("\n=== Validating Dependencies ===")
        for task_id, task_info in self.task_dependencies.items():
            for dep_id in task_info["depends_on"]:
                if dep_id not in self.task_dependencies:
                    error_msg = f"Missing dependency: {dep_id} required by {task_id}"
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)

        # Add maximum iteration limit
        MAX_ITERATIONS = 1000
        iteration = 0
        
        while any(not task["completed"] for task in self.task_dependencies.values()):
            iteration += 1
            if iteration > MAX_ITERATIONS:
                incomplete_tasks = [tid for tid, info in self.task_dependencies.items() 
                                  if not info["completed"]]
                error_msg = f"Maximum iterations exceeded. Tasks still pending: {incomplete_tasks}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            iteration_info = f"\nIteration {iteration}\nPending tasks: {[tid for tid, info in self.task_dependencies.items() if not info['completed']]}"
            self.logger.info(iteration_info)
            
            for task_id, task_info in self.task_dependencies.items():
                if task_info["completed"]:
                    continue

                # Check if all dependencies are completed
                if all(dep in self.results for dep in task_info["depends_on"]):
                    task_exec_info = f"\nExecuting task: {task_id}"
                    self.logger.info(task_exec_info)
                    
                    agent_spec = task_info["spec"]
                    llm_type = agent_spec.get("llm_type")
                    model = agent_spec.get("model")
                    task = agent_spec["task"]
                    
                    if "api_provider" in agent_spec:
                        provider = agent_spec.get("api_provider")
                        provider_info = f"  Using {provider} provider with model {model}"
                        self.logger.info(provider_info)
                        
                    config = {
                        "llm_type": llm_type,
                        "api_provider": provider,
                        "model": model
                    } if provider else {
                        "llm_type": llm_type,
                        "model": model
                    }

                    worker = WorkerAgent(config)
                    self.logger.info("  Starting worker execution...")
                    result = worker.handle_task(task)
                    self.logger.info("  Worker completed successfully")
                    
                    # Store the result with the full task ID
                    self.results[task_id] = result
                    task_info["completed"] = True
                    completion_info = f"  Task {task_id} marked as completed"
                    self.logger.info(completion_info)
                else:
                    waiting_info = f"  Task {task_id} waiting for dependencies: {[dep for dep in task_info['depends_on'] if dep not in self.results]}"
                    self.logger.info(waiting_info)

        completion_msg = "\n=== All Tasks Completed ==="
        self.logger.info(completion_msg)
        return self.results