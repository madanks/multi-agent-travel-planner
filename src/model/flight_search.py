"""
Flight search input schema.
"""
from typing import Optional
from pydantic import BaseModel, Field


class FlightSearchInput(BaseModel):
    """Input schema for flight search."""

    departure_airport: str = Field(...,
                                   description="Departure airport code (e.g., 'JFK')")
    arrival_airport: str = Field(...,
                                 description="Arrival airport code (e.g., 'LAX')")
    outbound_date: str = Field(..., description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(
        None, description="Return date (YYYY-MM-DD)")
    adults: int = Field(1, description="Number of adults")
    children: int = Field(0, description="Number of children")
    stops: Optional[int] = Field(
        None, description="0=Any, 1=Nonstop, 2=1 stop or fewer")
