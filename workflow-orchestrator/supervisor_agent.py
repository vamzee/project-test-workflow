import logging
from typing import TypedDict, Annotated, AsyncGenerator
from langgraph.graph import StateGraph, END
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    session_id: str
    user_message: str
    response: str
    error: str


class SupervisorAgent:
    def __init__(self, conversational_service_url='http://localhost:8001'):
        self.conversational_service_url = conversational_service_url
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("receive_request", self.receive_request)
        workflow.add_node("call_conversational_workflow", self.call_conversational_workflow)
        workflow.add_node("handle_response", self.handle_response)
        workflow.add_node("handle_error", self.handle_error)

        # Add edges
        workflow.set_entry_point("receive_request")
        workflow.add_edge("receive_request", "call_conversational_workflow")

        # Conditional edge based on whether call succeeded
        workflow.add_conditional_edges(
            "call_conversational_workflow",
            lambda state: "error" if state.get("error") else "success",
            {
                "success": "handle_response",
                "error": "handle_error"
            }
        )

        workflow.add_edge("handle_response", END)
        workflow.add_edge("handle_error", END)

        return workflow.compile()

    def receive_request(self, state: AgentState) -> AgentState:
        logger.info(f"Supervisor received request for session {state['session_id']}")
        return state

    def call_conversational_workflow(self, state: AgentState) -> AgentState:
        logger.info(f"Calling conversational workflow for session {state['session_id']}")

        try:
            response = requests.post(
                f"{self.conversational_service_url}/chat",
                json={
                    "session_id": state["session_id"],
                    "message": state["user_message"]
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                state["response"] = data.get("response", "")
                logger.info(f"Received response from conversational workflow")
            else:
                state["error"] = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Error from conversational workflow: {state['error']}")

        except Exception as e:
            state["error"] = str(e)
            logger.error(f"Failed to call conversational workflow: {e}")

        return state

    def handle_response(self, state: AgentState) -> AgentState:
        logger.info(f"Processing successful response for session {state['session_id']}")
        return state

    def handle_error(self, state: AgentState) -> AgentState:
        logger.error(f"Processing error for session {state['session_id']}: {state['error']}")
        state["response"] = f"Sorry, I encountered an error: {state['error']}"
        return state

    def process_request(self, session_id: str, user_message: str) -> str:
        initial_state = AgentState(
            session_id=session_id,
            user_message=user_message,
            response="",
            error=""
        )

        logger.info(f"Starting supervisor graph for session {session_id}")
        final_state = self.graph.invoke(initial_state)

        return final_state["response"]

    async def process_request_stream(self, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
        """Process request with streaming response"""
        logger.info(f"Starting supervisor streaming for session {session_id}")

        try:
            response = requests.post(
                f"{self.conversational_service_url}/chat/stream",
                json={
                    "session_id": session_id,
                    "message": user_message
                },
                stream=True,
                timeout=60
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if "chunk" in data:
                                yield data["chunk"]
                            elif "error" in data:
                                logger.error(f"Error from conversational workflow: {data['error']}")
                                yield f"Error: {data['error']}"
                                break
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode JSON: {e}")
                            continue
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Error from conversational workflow: {error_msg}")
                yield f"Sorry, I encountered an error: {error_msg}"

        except Exception as e:
            logger.error(f"Failed to call conversational workflow: {e}")
            yield f"Sorry, I encountered an error: {str(e)}"
