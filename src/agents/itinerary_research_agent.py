""" Itinerary research Agent """
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from constants.agent_constants import AgentConstants
from config.tavily_search_config import tavily_search_config

load_dotenv()


class ItineraryResearchAgent:
    """Itinerary Research Agent"""

    def __init__(self):
        """Create the itinerary research agent."""
        self.agent = create_deep_agent(
            model=init_chat_model(model=os.getenv(
                'OPENAI_LLM_MODEL'), model_provider="openai"),
            system_prompt=AgentConstants.RESEARCH_INSTRUCTION,
            tools=[tavily_search_config.internet_search],
        )


itinerary_research_agent = ItineraryResearchAgent()
