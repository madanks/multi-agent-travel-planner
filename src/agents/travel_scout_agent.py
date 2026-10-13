""" Travel scout Agent """
from langchain.agents import create_agent
from config.openai_config import llmconfig
from config.tavily_search_config import tavily_search_config
from constants.agent_constants import AgentConstants
from tools.itinerary_research_tool import call_itinerary_research_agent


class TravelScoutAgent:
    """Travel Scout Agent"""

    def __init__(self):
        """Create the travel scout agent."""
        self.agent = create_agent(
            model=llmconfig.llm,
            system_prompt=AgentConstants.TRAVEL_SCOUT_INSTRUCTIONS,
            tools=[tavily_search_config.internet_search,
                   call_itinerary_research_agent],
        )


travel_scout_agent = TravelScoutAgent()
