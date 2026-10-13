# multi-agent-travel-planner: Parallel Multi-Agent Travel Planning with LangGraph

A hands-on project for building a multi-agent travel planner with LangGraph and LangChain. A router reads the user's request, sends it to a flight/hotel search agent, a planner agent, or both in parallel, and a synthesizer merges the results into one answer. The agents use live tools: Google Flights and Google Hotels through SerpAPI, Tavily web search, and a deep research agent for itineraries.

---

## What's Inside

| Module                                    | Description                                                                                                                                                 |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/graph/travel_agent.py`               | Builds the LangGraph workflow: orchestrator, parallel search and planner agents with their tool loops, and the synthesizer. Includes a version with memory. |
| `src/node/agent_nodes.py`                 | Graph nodes: query router, search agent, planner agent, their tool executors, and the synthesizer.                                                          |
| `src/node/agent_edges.py`                 | Conditional edges: dispatches tasks to agents in parallel (Send API) and decides whether an agent loops back to its tools or moves on to the synthesizer.   |
| `src/agents/flight_hotel_search_agent.py` | Standalone agent that searches flights and hotels.                                                                                                          |
| `src/agents/itinerary_research_agent.py`  | Deep agent that researches a destination with Tavily and designs an itinerary.                                                                              |
| `src/agents/travel_scout_agent.py`        | General travel scout that answers high-level questions with web search and can hand itinerary requests to the research agent.                               |
| `src/tools/`                              | LangChain tools the agents call (see Tool Details below).                                                                                                   |
| `src/services/`                           | Service layer that talks to SerpAPI: builds the query, calls the API and trims the response.                                                                |
| `src/config/`                             | Connection settings for OpenAI, SerpAPI and Tavily, plus the LLM bound to the search and planner tools.                                                     |
| `src/model/`                              | Pydantic models: tool input schemas, the router's `ClassificationResult` and `AgentTask`.                                                                   |
| `src/state/`                              | LangGraph state definitions (`TravelPlannerState`, `AgentWorkerState`).                                                                                     |
| `src/constants/agent_constants.py`        | System prompts for the router, search agent, research agent, travel scout and synthesizer.                                                                  |
| `src/tests/test_agents.py`                | Live tests for the LLM connection, each tool, each agent and the full graph.                                                                                |

### How the graph works

```
START -> orchestrator --+--> search_agent_node  <-> search_tool_node  --+
                        |                                               +--> synthesizer -> END
                        +--> planner_agent_node <-> planner_tool_node --+
```

1. **Orchestrator** classifies the query and creates one or more tasks, each with a focused sub-query, and sets `requires_synthesis`.
2. **Dispatch** sends each task to its agent at the same time.
3. **Agents** call tools in a loop until they can answer without more tool calls.
4. **Synthesizer** returns a single result as is, or asks the LLM to merge several results into one organized response.

---

## Tool Details

| Tool                       | File                                   | What it does                                                                                                                                                 |
| -------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `search_flights`           | `src/tools/flight_search_tool.py`      | Google Flights search through SerpAPI. Takes departure and arrival airport codes, dates, passengers and stops. Returns up to 10 options with price and legs. |
| `search_hotels`            | `src/tools/hotel_search_tool.py`       | Google Hotels search through SerpAPI. Takes a location, dates, guests, rooms, star rating and sort order. Returns up to 5 hotels with price and rating.      |
| `tavily_search`            | `src/config/tavily_search_config.py`   | Tavily web search for current travel information such as attractions, seasons and transport.                                                                 |
| `itinerary_research_agent` | `src/tools/itinerary_research_tool.py` | Wraps the itinerary research agent as a tool so another agent can delegate a planning request to it.                                                         |

Tool groups:

- **Search agent tools:** `search_flights`, `search_hotels` (`src/tools/search_tools.py`).
- **Planner agent tools:** `tavily_search`, `itinerary_research_agent` (`src/tools/planner_tools.py`).

Each tool follows the same layering: a Pydantic input schema in `model/`, the API logic in `services/`, and a thin `@tool` wrapper in `tools/`. Service errors come back as a JSON `{"error": ...}` so the agent can read the failure.

---

## Key Learning Objectives

- **Multi-Agent Orchestration:** Route a request to one or several specialist agents with a structured-output router.
- **Parallel Execution:** Run agents at the same time with LangGraph's Send API and merge their results with a reducer (`operator.add`).
- **Tool-Calling Loops:** Bind tools to a model and loop between the agent node and the tool node until the model answers.
- **Agents as Tools:** Wrap one agent as a tool so another agent can delegate to it.
- **Service Layer Design:** Keep schemas, API logic and tool wrappers in separate layers so each can be tested and changed on its own.
- **Synthesis:** Combine several agent outputs into one organized answer.
- **Memory:** Keep conversation state across turns with a LangGraph checkpointer and a thread ID.
- **Safe Configuration:** Load API keys from a `.env` file and keep secrets out of the code.

---

## Quick Start

### Prerequisites

- **Python 3**
- An **OpenAI API key** and the name of the model to use
- A **SerpAPI key** (flight and hotel search)
- A **Tavily API key** (web search)

### Setup Instructions

#### 1. Clone & Set Up Virtual Environment

**macOS / Linux:**

```bash
git clone <repo-url>
cd multi-agent-travel-planner
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
git clone <your-repo-url>
cd multi-agent-travel-planner
py -3 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

#### 2. Install Dependencies

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Environment Configuration

Copy the template configuration file:

```bash
# macOS/Linux:
cp .env.example .env

# Windows (PowerShell):
Copy-Item .env.example .env
```

Set your API credentials in `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_LLM_MODEL=your_openai_model_name_here
SERPAPI_API_KEY=your_serpapi_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

#### 4. Run the Modules

Run everything from the `src/` folder so the `config`, `agents`, `graph` and other imports resolve.

Run the full test suite directly. It runs each agent and the whole graph in order:

```bash
cd src
python3 -m tests.test_agents
```

Run the graph on your own query:

```python
# from src/
from graph.travel_agent import build_parallel_travel_agent

agent = build_parallel_travel_agent()
result = agent.invoke({"user_query": "Plan a week in London and find me hotels under $200/night"})
print(result["final_answer"])
```

> The tests call the live OpenAI, Tavily and SerpAPI APIs, so they use your API credits. Start with `test_llm` and `test_tavily` to check your keys.
