"""
Itinerary research agent exposed as a tool.
"""
from langchain.tools import tool
from agents.itinerary_research_agent import itinerary_research_agent


@tool("itinerary_research_agent", description="plans travel itinerary")
def call_itinerary_research_agent(query: str) -> str:
    """Delegate a travel itinerary request to the itinerary research agent."""

    result = itinerary_research_agent.agent.invoke(
        {"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content
