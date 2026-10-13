"""
Flight search tool.
"""
import json
from typing import Optional
from langchain.tools import tool
from model.flight_search import FlightSearchInput
from services.flight_service import FlightService


@tool(args_schema=FlightSearchInput)
def search_flights(
    departure_airport: str,
    arrival_airport: str,
    outbound_date: str,
    return_date: Optional[str] = None,
    adults: int = 1,
    children: int = 0,
    stops: Optional[int] = None
) -> str:
    """Search for flights between airports."""

    try:
        return json.dumps(FlightService.search(
            departure_airport, arrival_airport, outbound_date,
            return_date, adults, children, stops))
    except Exception as e:  # pylint: disable=broad-exception-caught
        return json.dumps({"error": str(e)})
