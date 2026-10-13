"""
Flight search service: talks to SerpAPI Google Flights.
"""
import json
from typing import Optional
import requests
from serpapi import GoogleSearch
from serpapi.serp_api_client_exception import SerpApiClientException
from config.serpapi_config import serpapi_config

MAX_FLIGHTS = 10


class FlightService:
    """Searches flights through SerpAPI."""

    @staticmethod
    def build_params(
        departure_airport: str,
        arrival_airport: str,
        outbound_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        children: int = 0,
        stops: Optional[int] = None
    ) -> dict:
        """Build the SerpAPI query params for a flight search."""

        params = {
            'api_key': serpapi_config.api_key,
            'engine': 'google_flights',
            'departure_id': departure_airport.upper(),
            'arrival_id': arrival_airport.upper(),
            'outbound_date': outbound_date,
            'adults': adults,
            'children': children,
            'currency': serpapi_config.currency,
            'type': 1 if return_date else 2
        }

        if return_date:
            params['return_date'] = return_date
        if stops is not None:
            params['stops'] = stops

        return params

    @staticmethod
    def search(
        departure_airport: str,
        arrival_airport: str,
        outbound_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        children: int = 0,
        stops: Optional[int] = None
    ) -> str:
        """Search flights and return a trimmed result as a JSON string."""

        params = FlightService.build_params(
            departure_airport, arrival_airport, outbound_date,
            return_date, adults, children, stops)

        try:
            results = GoogleSearch(params).get_dict()
            flights = (results.get('best_flights', [])
                       + results.get('other_flights', []))
            if not flights:
                return json.dumps({"message": "No flights found"})

            output = [FlightService._format_flight(f)
                      for f in flights[:MAX_FLIGHTS]]
            return json.dumps(output, indent=2)

        except (SerpApiClientException, requests.RequestException, ValueError) as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def _format_airport(airport: dict) -> str:
        """Format an airport as '<code> <time>'."""
        return f"{airport.get('id')} {airport.get('time')}"

    @staticmethod
    def _format_flight(flight: dict) -> dict:
        """Trim a SerpAPI flight option down to the fields the agent needs."""
        return {
            "price": flight.get("price"),
            "duration_mins": flight.get("total_duration"),
            "airline_logo": flight.get("airline_logo"),
            "legs": [{
                "airline": leg.get("airline"),
                "flight_number": leg.get("flight_number"),
                "departure": FlightService._format_airport(
                    leg.get("departure_airport", {})),
                "arrival": FlightService._format_airport(
                    leg.get("arrival_airport", {})),
                "airline_logo": leg.get("airline_logo")
            } for leg in flight.get("flights", [])]
        }
