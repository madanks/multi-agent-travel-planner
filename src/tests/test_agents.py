"""
Live tests for the agents (these call the real OpenAI, Tavily and SerpAPI APIs).
"""
import os
import pytest
from dotenv import load_dotenv

load_dotenv()

# pylint: disable=wrong-import-position
from config.openai_config import llmconfig  # noqa: E402
from config.tavily_search_config import tavily_search_config  # noqa: E402
from agents.itinerary_research_agent import itinerary_research_agent  # noqa: E402
from agents.flight_hotel_search_agent import flight_hotel_search_agent  # noqa: E402
from agents.travel_scout_agent import travel_scout_agent  # noqa: E402
from graph.travel_agent import build_parallel_travel_agent, build_parallel_travel_agent_with_persistence  # noqa: E402


pytestmark = pytest.mark.skipif(
    not all(os.getenv(k) for k in (
        "OPENAI_API_KEY", "OPENAI_LLM_MODEL", "TAVILY_API_KEY", "SERPAPI_API_KEY")),
    reason="API keys missing in environment/.env")


def user_message(content: str) -> dict:
    """Wrap a user query in the agent input format."""
    return {"messages": [{"role": "user", "content": content}]}


class TestAgents:
    """Tests for the LLM connection, search tools and agents."""

    def test_llm(self):
        """Test LLM communication"""
        test_msg = llmconfig.llm.invoke(
            "What is Machine Learning? Explain with the help of an example.")
        print(test_msg.text)
        assert test_msg.text

    def test_tavily(self):
        """Test Tavily connection"""
        test_msg = tavily_search_config.internet_search.invoke(
            {"query": "Top Travel attractions in Vienna"})
        print(test_msg)
        assert test_msg

    def test_itinerary_agent(self):
        """Test Itinerary Agent"""
        result = itinerary_research_agent.agent.invoke(user_message(
            "Plan a 5 day travel iternerary for a food & hstorical sites lover during winter in Delhi"))
        print(result["messages"][-1].content[-1])
        assert result["messages"][-1].content

    def test_flight_search_agent(self):
        """Test the flight search through the search agent"""
        result = flight_hotel_search_agent.agent.invoke(user_message(
            "Find me flight, returning on January 22, 2027 from New York to London on January 18, 2026 for 1 adults only"))
        print(result["messages"][-1].content[-1])
        assert result["messages"][-1].content

    def test_hotel_search_agent(self):
        """Test the hotel search through the search agent"""
        result = flight_hotel_search_agent.agent.invoke(user_message(
            "Find me hotels on January 22, 2027 in London for 1 adults only for 2 nights"))
        print(result["messages"][-1].content[-1])
        assert result["messages"][-1].content

    def test_travel_scout_agent_internet_search(self):
        """Test the travel scout agent answering with internet search"""
        result = travel_scout_agent.agent.invoke(user_message(
            "What is the best season to travel to Jodhpur?"))
        print(result["messages"][-1].content[-1])
        assert result["messages"][-1].content

    def test_travel_scout_agent_research_itinerary(self):
        """Test the travel scout agent delegating to the itinerary research agent"""
        result = travel_scout_agent.agent.invoke(user_message(
            "Plan 2 day itinerary for Agra travel for a history & culture lover, also want to try special cusine to this city"))
        print(result["messages"][-1].content[-1])
        assert result["messages"][-1].content

    def test_stream_events(self):
        """Test streaming the travel scout agent events"""
        chunks = list(travel_scout_agent.agent.stream(user_message(
            "What is the best season to travel to Jodhpur?")))
        for chunk in chunks:
            print(chunk)
        assert chunks

    def test_stream_events_with_pretty_print(self):
        """Test streaming the travel scout agent events with pretty print"""
        events = list(travel_scout_agent.agent.stream(
            user_message(
                "Plan 2 day itinerary for Agra travel for a history & culture lover, also want to try special cusine to this city"),
            stream_mode="values"))
        for event in events:
            print(event)
            event["messages"][-1].pretty_print()
        assert events

    def test_multi_agent_travel_planner(self):
        """Test Multi-Agent Travel Planner"""
        agent = build_parallel_travel_agent()
        result = agent.invoke({
            "user_query": "Plan a 5-day trip to Paris and find me flights from JFK to LHR for 1 adult only on 21 Jan 2027 (one way trip) & also let me know hotels for myself only (adult) from my lading to LHR to next day",
            "messages": []
        })

        # Print everything step by step
        print("=" * 60)
        print("USER QUERY:")
        print(result["user_query"])

        print("\n" + "=" * 60)
        print("TASKS DISPATCHED:")
        for task in result.get("tasks", []):
            print(f"  • {task.source}: {task.user_query}")

        print("\n" + "=" * 60)
        print("AGENT RESULTS:")
        for r in result.get("agent_results", []):
            print(f"\n[{r['agent'].upper()}]")
            print("-" * 40)
            for s in r["result"]:
                if (s["type"] == "text"):
                    print(s["text"])

        print("\n" + "=" * 60)
        print("FINAL SYNTHESIZED RESPONSE:")
        print("=" * 60)
        print(result["final_answer"])

    def test_multi_agent_travel_planner_with_persistence(self):
        """Test Multi-Agent Travel Planner with persistence"""
        agent = build_parallel_travel_agent_with_persistence()
        config = {"configurable": {"thread_id": "user-01"}}
        result = agent.invoke(
            {
                "user_query": "What is the best time to visit Kathmandu?",
                "messages": [],
                "tasks": [],
                "requires_synthesis": False,
                "agent_results": [],
                "final_answer": "",
                "search_messages": [],
                "planner_messages": [],
            },
            config=config
        )
        for s in result['final_answer']:
            if (s["type"] == "text"):
                print(s["text"])
        print("\n" + "=" * 60)
        result1 = agent.invoke(
            {
                "user_query": "Major historical sites there (must visit kind of)",
                "messages": [],
                "tasks": [],
                "requires_synthesis": False,
                "agent_results": [],
                "final_answer": "",
                "search_messages": [],
                "planner_messages": [],
            },
            config=config
        )
        print(result1['final_answer'])
        print("\n" + "=" * 60)
        result2 = agent.invoke(
            {
                "user_query": "What all cities I can cover along with this tour (in nearby which should not take more than 2-3 days extra)",
                "messages": [],
                "tasks": [],
                "requires_synthesis": False,
                "agent_results": [],
                "final_answer": "",
                "search_messages": [],
                "planner_messages": [],
            },
            config=config
        )
        print(result2['final_answer'])

    @staticmethod
    def save_graph_png(agent, filename: str):
        """Save the graph view of an agent as a PNG (helper, not a test)"""
        image_bytes = agent.get_graph().draw_mermaid_png()
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename, "wb") as f:
            f.write(image_bytes)


def main():
    """Run the tests directly: python3 -m tests.test_agents"""
    tests = TestAgents()
    separator = "\n" + "=" * 80 + "\n"

    tests.test_llm()
    print(separator)
    tests.test_tavily()
    print(separator)
    tests.test_itinerary_agent()
    print(separator)
    tests.save_graph_png(itinerary_research_agent.agent,
                         "itinerary__agent_graph.png")
    tests.test_flight_search_agent()
    print(separator)
    tests.test_hotel_search_agent()
    print(separator)
    tests.save_graph_png(flight_hotel_search_agent.agent,
                         "search_agent_graph.png")
    tests.test_travel_scout_agent_internet_search()
    print(separator)
    tests.test_travel_scout_agent_research_itinerary()
    print(separator)
    tests.test_stream_events()
    print(separator)
    tests.test_stream_events_with_pretty_print()
    print(separator)
    tests.save_graph_png(build_parallel_travel_agent(),
                         "travel_agent_graph.png")
    print(separator)
    tests.test_multi_agent_travel_planner()
    print(separator)
    tests.test_multi_agent_travel_planner_with_persistence()


if __name__ == "__main__":
    main()
