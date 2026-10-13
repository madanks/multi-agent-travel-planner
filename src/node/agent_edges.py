"""
Agent edges: conditional routing between graph nodes
"""
from langgraph.types import Send
from state.travel_planner import TravelPlannerState


class AgentEdges:
    """Agent conditional edges."""

    @staticmethod
    def dispatch_to_agents(state: TravelPlannerState):
        """
        Uses Send API to dispatch tasks to agents in PARALLEL.
        This is the key function that enables concurrent execution.
        """
        tasks = state.get("tasks", [])

        sends = []
        for task in tasks:

            worker_state = {
                "messages": state.get("messages", []),
                "user_query": task.user_query,
                "tasks": state.get("tasks", []),
                "requires_synthesis": state.get("requires_synthesis", False),
                "agent_results": [],  # Each worker starts fresh
                "final_answer": "",
                "search_messages": [],  # Initialize empty for workers
                "planner_messages": [],  # Initialize empty for workers
            }

            if task.source == "search_agent_node":
                # Your existing node
                sends.append(Send("search_agent_node", worker_state))
            elif task.source == "planner_agent_node":
                # Your existing node
                sends.append(Send("planner_agent_node", worker_state))

        return sends

    @staticmethod
    def should_continue_for_search_agent(state: TravelPlannerState):
        """Check if search agent needs to continue tool loop"""
        search_msgs = state.get("search_messages", [])
        if search_msgs and hasattr(search_msgs[-1], 'tool_calls') and search_msgs[-1].tool_calls:
            return "search_tool_node"
        return "synthesizer"

    @staticmethod
    def should_continue_for_planner_agent(state: TravelPlannerState):
        """Check if planner needs to continue tool loop"""
        planner_msgs = state.get("planner_messages", [])
        if planner_msgs and hasattr(planner_msgs[-1], 'tool_calls') and planner_msgs[-1].tool_calls:
            return "planner_tool_node"
        return "synthesizer"
