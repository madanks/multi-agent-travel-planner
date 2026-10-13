""" Flight and hotel search Agent """
from langchain.agents import create_agent
from config.openai_config import llmconfig
from constants.agent_constants import AgentConstants
from tools.search_tools import search_tools


class FlightHotelSearchAgent:
    """Flight and Hotel Search Agent"""

    def __init__(self):
        """Create the flight and hotel search agent."""
        self.agent = create_agent(
            model=llmconfig.llm,
            tools=search_tools,
            system_prompt=AgentConstants.FLIGHT_HOTEL_SEARCH_INSTRUCTION,
        )


flight_hotel_search_agent = FlightHotelSearchAgent()
