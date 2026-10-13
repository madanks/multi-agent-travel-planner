"""
OpenAI config to connect to llm 
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


class OpenAIConfig:
    "OpenAI connection"

    def __init__(self):
        """Create the ChatOpenAI client from environment variables."""
        self.llm = ChatOpenAI(
            model=os.getenv('OPENAI_LLM_MODEL'),
            # stream_usage=True,
            # temperature=0.2,
            # max_tokens=None,
            # timeout=None,
            # reasoning_effort="low",
            # max_retries=2,
            api_key=os.getenv('OPENAI_API_KEY'),
            # base_url="...",
            # organization="...",
            # other params...
        )


llmconfig = OpenAIConfig()
