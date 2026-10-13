"""
SerpAPI config
"""
import os
from dotenv import load_dotenv

load_dotenv()


class SerpApiConfig:
    "SerpAPI connection"

    def __init__(self):
        """Read the SerpAPI settings from environment variables."""
        self.api_key = os.getenv('SERPAPI_API_KEY')
        self.currency = 'USD'


serpapi_config = SerpApiConfig()
