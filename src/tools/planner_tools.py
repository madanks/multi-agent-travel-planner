"""
Planner agent tools.
"""
from config.tavily_search_config import tavily_search_config
from tools.itinerary_research_tool import call_itinerary_research_agent

planner_tools = [tavily_search_config.internet_search,
                 call_itinerary_research_agent]
planner_tools_by_name = {tool.name: tool for tool in planner_tools}
