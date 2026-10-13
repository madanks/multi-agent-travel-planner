"""
Travel planner graph with parallel agent execution
"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from state.travel_planner import TravelPlannerState
from node.agent_nodes import AgentNodes
from node.agent_edges import AgentEdges


def __build_travel_graph() -> StateGraph:
    """Build the (uncompiled) graph builder with parallel execution support."""

    builder = StateGraph(TravelPlannerState)

    # Add nodes
    builder.add_node("orchestrator", AgentNodes.classify_query_parallel)
    builder.add_node("search_agent_node", AgentNodes.search_agent_node)
    builder.add_node("planner_agent_node", AgentNodes.planner_agent_node)
    builder.add_node("search_tool_node", AgentNodes.search_tool_node)
    builder.add_node("planner_tool_node", AgentNodes.planner_tool_node)
    builder.add_node("synthesizer", AgentNodes.synthesizer_node)

    # Connect edges
    builder.add_edge(START, "orchestrator")

    # Router dispatches to agents via Send API (parallel execution)
    builder.add_conditional_edges(
        "orchestrator",
        AgentEdges.dispatch_to_agents,
        ["search_agent_node", "planner_agent_node"]
    )

    # Search agent tool loop
    builder.add_conditional_edges(
        "search_agent_node",
        AgentEdges.should_continue_for_search_agent,
        ["search_tool_node", "synthesizer"]  # Go to synthesizer instead of END
    )
    builder.add_edge("search_tool_node", "search_agent_node")

    # Planner agent tool loop
    builder.add_conditional_edges(
        "planner_agent_node",
        AgentEdges.should_continue_for_planner_agent,
        # Go to synthesizer instead of END
        ["planner_tool_node", "synthesizer"]
    )
    builder.add_edge("planner_tool_node", "planner_agent_node")

    # End after synthesis
    builder.add_edge("synthesizer", END)

    return builder


def build_parallel_travel_agent():
    """Build the graph with parallel execution support."""

    return __build_travel_graph().compile()


def build_parallel_travel_agent_with_persistence():
    """Build the graph with parallel execution support with persistence."""

    builder = __build_travel_graph()

    # Built-in Persistence
    checkpointer = InMemorySaver()

    return builder.compile(checkpointer=checkpointer)
