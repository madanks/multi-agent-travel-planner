"""
Router output: the agent tasks to run and whether synthesis is needed.
"""
from typing import List
from pydantic import BaseModel, Field
from model.agent_task import AgentTask


class ClassificationResult(BaseModel):
    """Router output - now supports MULTIPLE parallel tasks."""
    tasks: List[AgentTask] = Field(
        description="List of agents to invoke with their targeted queries"
    )
    requires_synthesis: bool = Field(
        default=False,
        description="Whether multiple agents are being used and synthesis is needed"
    )
