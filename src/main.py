import sys
import argparse
from pathlib import Path
import ast
import uuid

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from agents.router import Router
from agents.manager import ManagerAgent
from agents.worker import WorkerAgent
from src.utils.logging import setup_logging

def main():
    # Setup logging
    logger = setup_logging()
    logger.info("\n=== TaskMaestro Starting ===")
    
    parser = argparse.ArgumentParser(description="Run TaskMaestro with custom LLM config.")
    
    # Add task as both positional and optional argument
    parser.add_argument("task", nargs="?", help="The task to execute")
    parser.add_argument("--task", "-t", dest="task_arg", help="The task to execute")
    
    # LLM configuration arguments
    parser.add_argument("--type", "-l", dest="llm_type", required=True, help="LLM type: 'api' or 'local'")
    parser.add_argument("--provider", "-p", dest="api_provider", required=False, help="LLM provider, e.g., 'openai', 'ollama'")
    parser.add_argument("--model", "-m", required=True, help="LLM model name")

    args = parser.parse_args()
    config_info = f"\nConfiguration:\n  LLM Type: {args.llm_type}\n  Provider: {args.api_provider}\n  Model: {args.model}"
    logger.info(config_info)
    
    # Use the task from either positional or named argument
    task = args.task_arg if args.task_arg else args.task
    if not task:
        task = "How to bake a cake"  # Default task if none provided
    
    task_info = f"\nTask: {task}"
    logger.info(task_info)
    
    router = Router()
    
    manager_config = {
        "llm_type": args.llm_type,
        "api_provider": args.api_provider,
        "model": args.model
    }
    manager = ManagerAgent(manager_config)
    manager_info = f"\nManager Agent initialized with ID: {manager.id}"
    logger.info(manager_info)

    previous_results = None
    iteration = 0
    
    while True:
        iteration += 1
        iteration_info = f"\n=== Starting Iteration {iteration} ==="
        logger.info(iteration_info)
        
        # Get manager's plan
        logger.info("\nRequesting task plan from manager...")
        manager_output = manager.plan_task(task, previous_results)
        logger.info("Received plan from manager")
        
        # Execute the plan
        logger.info("\nExecuting manager's plan...")
        results = router.execute_manager_output(manager_output)
        
        # Check if any tasks need to be repeated
        logger.info("\nChecking for tasks that need repetition...")
        payload = ast.literal_eval(manager_output)
        needs_repetition = False
        
        for agent_spec in payload["agents"]:
            if "repeat_condition" in agent_spec:
                agent_id = agent_spec.get("agent_id", f"worker-{uuid.uuid4().hex[:8]}")
                task_id = agent_spec.get("task_id", str(uuid.uuid4().hex[:8]))
                full_task_id = f"{agent_id}_{task_id}"
                
                if full_task_id in results:
                    logger.info(f"\nChecking repeat condition for task {full_task_id}")
                    # Evaluate the repeat condition using the task's result
                    condition = agent_spec["repeat_condition"]
                    if eval(condition, {"result": results[full_task_id]}):
                        logger.info(f"  Task {full_task_id} needs to be repeated")
                        needs_repetition = True
                        break
                    else:
                        logger.info(f"  Task {full_task_id} does not need repetition")
        
        if not needs_repetition:
            logger.info("\nNo tasks need repetition, proceeding to final aggregation")
            break
            
        # Update previous results for the next iteration
        previous_results = results
        # You might want to modify the task based on the results
        task = f"Continue with the previous task, incorporating these results: {results}"
        logger.info(f"\nUpdated task for next iteration: {task}")

    # Aggregate all results into a final output
    logger.info("\n=== Aggregating Final Results ===")
    final_output = manager.aggregate_results(task, results)
    
    completion_msg = "\n=== TaskMaestro Completed Successfully ==="
    logger.info(completion_msg)
    
    logger.info("\nFinal Output:")
    logger.info(final_output)
    
if __name__ == "__main__":
    main()
    
# python src/main.py "Write a story about a robot" --type api -p anthropic -m claude-3-5-sonnet-20240620