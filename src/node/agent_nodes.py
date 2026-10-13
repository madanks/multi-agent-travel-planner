"""
Agent nodes
"""
from langchain.messages import SystemMessage, ToolMessage, HumanMessage, AIMessage
from state.travel_planner import TravelPlannerState
from constants.agent_constants import AgentConstants
from config.openai_config import llmconfig
from config.tool_models_config import tool_models_config
from tools.search_tools import search_tools_by_name
from tools.planner_tools import planner_tools_by_name
from model.classification_result import ClassificationResult


class AgentNodes:
    """Agent nodes."""

    @staticmethod
    def classify_query_parallel(state: TravelPlannerState) -> dict:
        """
        Updated router that can dispatch to MULTIPLE agents.
        """
        router_llm = llmconfig.llm
        structured_llm = router_llm.with_structured_output(
            ClassificationResult)

        result = structured_llm.invoke([
            {"role": "system", "content": AgentConstants.ROUTER_INSTRUCTION},
            {"role": "user", "content": state["user_query"]}
        ])

        return {
            "tasks": result.tasks,
            "requires_synthesis": result.requires_synthesis
        }

    @staticmethod
    def search_agent_node(state: TravelPlannerState):
        """Search agent with its own message history"""

        # Use search-specific messages
        search_msgs = state.get("search_messages", [])

        messages = [SystemMessage(
            content=AgentConstants.FLIGHT_HOTEL_SEARCH_INSTRUCTION)] + search_msgs

        # If this is first call, add the user query
        if not search_msgs:
            messages.append(HumanMessage(content=state.get("user_query", "")))

        response = tool_models_config.search_model_with_tools.invoke(messages)

        return {
            "search_messages": [response],
            "agent_results": [{
                "agent": "search_agent",
                "focus": "flights and hotels",
                "result": response.content
            }] if not response.tool_calls else []
        }

    @staticmethod
    def search_tool_node(state: TravelPlannerState):
        """Execute search tools"""
        search_msgs = state.get("search_messages", [])

        # Check if search_messages exists and has content
        if not search_msgs:
            return {"search_messages": []}

        last_message = search_msgs[-1]

        # Check if last_message has tool_calls
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return {"search_messages": []}

        result = []
        for tool_call in last_message.tool_calls:
            tool = search_tools_by_name.get(tool_call["name"])
            if tool:
                observation = tool.invoke(tool_call["args"])
                result.append(ToolMessage(content=observation,
                              tool_call_id=tool_call["id"]))

        return {"search_messages": result}

    @staticmethod
    def planner_agent_node(state: TravelPlannerState):
        """Planner agent with its own message history"""

        # Use planner-specific messages
        planner_msgs = state.get("planner_messages", [])

        messages = [SystemMessage(
            content=AgentConstants.TRAVEL_SCOUT_INSTRUCTIONS)] + planner_msgs

        # If this is first call, add the user query
        if not planner_msgs:
            messages.append(HumanMessage(content=state.get("user_query", "")))

        response = tool_models_config.planner_model_with_tools.invoke(messages)

        return {
            "planner_messages": [response],
            "agent_results": [{
                "agent": "planner_agent",
                "focus": "travel planning and itinerary",
                "result": response.content
            }] if not response.tool_calls else []
        }

    @staticmethod
    def planner_tool_node(state: TravelPlannerState):
        """Execute planner tools"""
        planner_msgs = state.get("planner_messages", [])

        # Check if planner_messages exists and has content
        if not planner_msgs:
            return {"planner_messages": []}

        last_message = planner_msgs[-1]

        # Check if last_message has tool_calls
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return {"planner_messages": []}

        result = []

        for tool_call in last_message.tool_calls:
            tool = planner_tools_by_name.get(tool_call["name"])
            if tool:
                observation = tool.invoke(tool_call["args"])
                result.append(ToolMessage(content=observation,
                              tool_call_id=tool_call["id"]))

        return {"planner_messages": result}

    @staticmethod
    def synthesizer_node(state: TravelPlannerState) -> dict:
        """
        Combines results from parallel agents into a unified response.
        Only called when requires_synthesis is True.
        """

        agent_results = state.get("agent_results", [])

        if not agent_results:
            return {
                "final_answer": "I couldn't process your request.",
                "messages": [AIMessage(content="I couldn't process your request.")]
            }

        # If only one result, no synthesis needed
        if len(agent_results) == 1:
            result = agent_results[0]["result"]
            return {
                "final_answer": result,
                "messages": [AIMessage(content=result)]
            }

        # Format results for synthesis
        results_formatted = "\n\n" + "="*50 + "\n\n".join([
            f"**{r['agent'].upper()}**\nFocus: {r.get('focus', 'N/A')}\n\n{r['result']}"
            for r in agent_results
        ])

        response = llmconfig.llm.invoke([
            HumanMessage(content=AgentConstants.SYNTHESIZER_INSTRUCTION.format(
                query=state["user_query"],
                results=results_formatted
            ))
        ])

        return {
            "final_answer": response.content,
            "messages": [AIMessage(content=response.content)]
        }
