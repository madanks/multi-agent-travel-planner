"""
Agent Worker State
"""
from typing import TypedDict, Annotated, List
import operator
from langchain.messages import AnyMessage
from model.agent_task import AgentTask


class AgentWorkerState(TypedDict):
    """State passed to each parallel worker."""
    task: AgentTask
    messages: List[AnyMessage]
    agent_results: Annotated[List[dict], operator.add]
