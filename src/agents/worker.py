import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.llm.access import LLMAccess
import uuid
from datetime import datetime, timezone

class WorkerAgent:
    def __init__(self, config: dict):
        self.id = f"worker-{uuid.uuid4().hex[:8]}"
        self.llm = LLMAccess(config)
        self.role_description = """
        You are a WorkerAgent. Your job is to complete the task you are given with clarity, precision, and autonomy.

        - Assume the task is atomic, meaning it is specific and does not require delegation or planning.
        - Execute the task to the best of your ability.
        - Your response should be concise, accurate, and structured.
        - If code is requested, format it properly.
        - If explanation is requested, provide it clearly and step-by-step.
        - If lists or instructions are requested, format them cleanly and logically.

        Do not ask questions or request clarification. You are confident in your response and can work independently.
        """

    def assess_atomicity(self, task: str) -> bool:
        assessment_prompt = f"""
        Determine whether the following task is atomic.

        A task is atomic if:
        - It has one clear goal or instruction, not a list of steps or goals.
        - It does not contain multiple steps or goals.
        - It can be completed by a single agent in one response.
        - It does not require planning, decomposition, or delegation.
        
        Respond with only one word: "atomic" or "not atomic". No punctuation.
        """

        result = self.llm.call(task, role_description=assessment_prompt).strip().lower()
        
        if result == "atomic" or result == "not atomic":
            return result
        else:
            raise ValueError("Invalid atomicity response from LLM")

    def handle_task(self, task: str) -> str:
        if self.assess_atomicity(task) == "atomic":
            return self.llm.call(task, role_description=self.role_description)
        else:
            # raise ValueError("Task is not atomic")
            return "Task is not atomic", task