"""
This class is a Agent Task with targeted query.
"""
from typing import Literal
from pydantic import BaseModel


class AgentTask(BaseModel):
    """A single agent task with targeted query."""
    source: Literal["search_agent_node", "planner_agent_node"]
    user_query: str
    focus: str = ""  # What aspect this agent should focus on
