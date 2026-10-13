"""
Search agent tools.
"""
from tools.flight_search_tool import search_flights
from tools.hotel_search_tool import search_hotels

search_tools = [search_flights, search_hotels]
search_tools_by_name = {tool.name: tool for tool in search_tools}
