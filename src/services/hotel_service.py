"""
Hotel search service: talks to SerpAPI Google Hotels.
"""
import json
from typing import Optional
import requests
from serpapi import GoogleSearch
from serpapi.serp_api_client_exception import SerpApiClientException
from config.serpapi_config import serpapi_config

MAX_HOTELS = 5


class HotelService:
    """Searches hotels through SerpAPI."""

    @staticmethod
    def build_params(
        location: str,
        check_in_date: str,
        check_out_date: str,
        adults: int = 1,
        children: int = 0,
        rooms: int = 1,
        hotel_class: Optional[str] = None,
        sort_by: int = 8
    ) -> dict:
        """Build the SerpAPI query params for a hotel search."""

        params = {
            'api_key': serpapi_config.api_key,
            'engine': 'google_hotels',
            'q': location,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'adults': adults,
            'children': children,
            'rooms': rooms,
            'sort_by': sort_by,
            'currency': serpapi_config.currency,
            'hl': 'en',
            'gl': 'us'
        }

        if hotel_class:
            params['hotel_class'] = hotel_class

        return params

    @staticmethod
    def search(
        location: str,
        check_in_date: str,
        check_out_date: str,
        adults: int = 1,
        children: int = 0,
        rooms: int = 1,
        hotel_class: Optional[str] = None,
        sort_by: int = 8
    ) -> str:
        """Search hotels and return a trimmed result as a JSON string."""

        params = HotelService.build_params(
            location, check_in_date, check_out_date, adults,
            children, rooms, hotel_class, sort_by)

        try:
            results = GoogleSearch(params).get_dict()
            properties = results.get('properties', [])
            if not properties:
                return json.dumps({"message": "No hotels found"})

            output = [HotelService._format_hotel(h)
                      for h in properties[:MAX_HOTELS]]
            return json.dumps(output, indent=2)

        except (SerpApiClientException, requests.RequestException, ValueError) as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def _format_hotel(hotel: dict) -> dict:
        """Trim a SerpAPI hotel property down to the fields the agent needs."""
        images = hotel.get("images")
        return {
            "name": hotel.get("name"),
            "price": hotel.get("rate_per_night", {}).get("lowest"),
            "rating": hotel.get("overall_rating"),
            "reviews": hotel.get("reviews"),
            "stars": hotel.get("hotel_class"),
            "thumbnail": images[0].get("thumbnail") if images else None
        }
