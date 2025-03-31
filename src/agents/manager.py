from datetime import datetime, timezone
import uuid

import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.llm.access import LLMAccess
from src.utils.available_models import get_available_api_providers, get_available_local_models

class ManagerAgent:
    def __init__(self, config):
        self.id = f"manager-{uuid.uuid4().hex[:8]}"
        self.llm = LLMAccess(config)
        self.role_description = f"""
        You are a strategic, detail-oriented, and highly organized project manager agent with ID {self.id}.

        Your job is to:
        - Analyze a high-level task
        - If it is complex and requires multiple steps, break it down into atomic subtasks
        - Assign each subtask to a new agent
        - Choose the best LLM provider and model for each agent to best complete the task
        - Identify dependencies between tasks and specify which tasks must complete before others can begin
        - Determine if any tasks should be repeated based on their results
        - Aggregate and format the results from all workers to satisfy the original task requirements

        Your output must be a JSON list of agent configurations. Each item must include:
        - task_id: A unique identifier for the task (will be prefixed with agent ID)
        - agent_id: A unique identifier for the agent (format: "worker-{uuid}")
        - depends_on: List of task_ids that must complete before this task can begin
        - llm_type: "api" or "local"
        - api_provider: One of the available providers listed below
        - model: One available model per provider
        - task: A clear, specific instruction for the agent
        - repeat_condition: (optional) A condition that determines if this task should be repeated
        - output_format: (optional) The format in which the worker should provide their output (e.g., "json", "text", "code")

        Available API models: {get_available_api_providers()}
        Available local models: {get_available_local_models()}

        Respond only with valid JSON format. Nothing else.
        The format should be \"\"\"{{\"agents\": [...]}}\"\"\"
        """

    def plan_task(self, task: str, previous_results: dict = None) -> str:
        # Include previous results in the prompt if available
        context = f"Previous task results: {previous_results}" if previous_results else ""
        return self.llm.call(f"{task}\n\n{context}", role_description=self.role_description)

    def aggregate_results(self, task: str, results: dict) -> str:
        """
        Aggregate and format the results from all workers to satisfy the original task.
        """
        aggregation_prompt = f"""
        You are a result aggregation specialist. Your job is to combine the outputs from multiple workers into a single, coherent response that satisfies the original task.

        Original task: {task}

        Worker results: {results}

        Combine these results into a single response that:
        1. Satisfies the original task requirements
        2. Maintains the logical flow and structure needed
        3. Removes any JSON formatting or technical artifacts
        4. Presents the information in a clear, natural format

        Respond with the aggregated result in the format required by the original task.
        Do not include any JSON formatting or technical artifacts in the final output.
        """

        return self.llm.call(aggregation_prompt, role_description=aggregation_prompt)