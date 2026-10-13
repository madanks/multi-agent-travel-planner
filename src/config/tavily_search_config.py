"""
OpenAI config to connect to llm 
"""
import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()


class TavilySearchConfig:
    "TavilySearch connection"

    def __init__(self):
        """Create the Tavily search tool from environment variables."""
        self.internet_search = TavilySearch(
            max_results=5,
            topic="general",
            # include_answer=False,
            # include_raw_content=False,
            include_images=True,
            include_image_descriptions=True,
            search_depth="advanced",
            # time_range="day",
            # include_domains=None,
            # exclude_domains=None,
            api_key=os.getenv('TAVILY_API_KEY'),
        )


tavily_search_config = TavilySearchConfig()
