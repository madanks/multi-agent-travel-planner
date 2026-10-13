"""
LLM bound with the search and planner tools
"""
from config.openai_config import llmconfig
from tools.search_tools import search_tools
from tools.planner_tools import planner_tools


class ToolModelsConfig:
    "LLM augmented with tools"

    def __init__(self):
        """Bind the search and planner tools to the LLM."""
        self.search_model_with_tools = llmconfig.llm.bind_tools(search_tools)
        self.planner_model_with_tools = llmconfig.llm.bind_tools(
            planner_tools)


tool_models_config = ToolModelsConfig()
