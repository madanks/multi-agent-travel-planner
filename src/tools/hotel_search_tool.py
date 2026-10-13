"""
Hotel search tool.
"""
from typing import Optional
from langchain.tools import tool
from model.hotel_search import HotelSearchInput
from services.hotel_service import HotelService


@tool(args_schema=HotelSearchInput)
def search_hotels(
    location: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 1,
    children: int = 0,
    rooms: int = 1,
    hotel_class: Optional[str] = None,
    sort_by: int = 8
) -> str:
    """Search for hotels in a location."""

    return HotelService.search(
        location, check_in_date, check_out_date, adults,
        children, rooms, hotel_class, sort_by)
