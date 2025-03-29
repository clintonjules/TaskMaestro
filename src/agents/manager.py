from datetime import datetime, timezone
import uuid

import sys
from typing import Dict
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
        You are a strategic, detail-oriented, and highly organized project manager agent.

        Your job is to:
        - Analyze a high-level task
        - If it is complex and requires multiple steps, break it down into atomic subtasks
        - Assign each subtask to a new agent
        - Choose the best LLM provider and model for each agent to best complete the task

        Your output must be a JSON list of agent configurations. Each item must include:
        - llm_type: "api" or "local"
        - api_provider: One of the available providers listed below
        - model: One available model per provider
        - role: "worker" or "manager"
        - role_description: A clear system message for the new agent
        - task: A clear, specific instruction for the agent
        - reason: The reason you chose the model you did

        Available API models: {get_available_api_providers()}
        Available local models: {get_available_local_models()}

        Respond only with valid JSON format.
        """

    def plan_task(self, task: str) -> str:
        return self.llm.call(task, role_description=self.role_description)