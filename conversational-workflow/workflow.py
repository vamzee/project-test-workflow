import logging
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversationState(TypedDict):
    session_id: str
    message: str
    chat_history: List[Dict[str, str]]
    response: str


class ConversationalWorkflow:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=self.api_key
        )

        self.graph = self._build_graph()
        self.session_histories: Dict[str, List[Dict[str, str]]] = {}

    def _build_graph(self):
        workflow = StateGraph(ConversationState)

        # Add nodes
        workflow.add_node("prepare_messages", self.prepare_messages)
        workflow.add_node("call_llm", self.call_llm)
        workflow.add_node("format_response", self.format_response)

        # Add edges
        workflow.set_entry_point("prepare_messages")
        workflow.add_edge("prepare_messages", "call_llm")
        workflow.add_edge("call_llm", "format_response")
        workflow.add_edge("format_response", END)

        return workflow.compile()

    def prepare_messages(self, state: ConversationState) -> ConversationState:
        session_id = state["session_id"]

        # Get or initialize chat history for this session
        if session_id not in self.session_histories:
            self.session_histories[session_id] = []

        state["chat_history"] = self.session_histories[session_id]
        logger.info(f"Prepared messages for session {session_id}")

        return state

    def call_llm(self, state: ConversationState) -> ConversationState:
        logger.info(f"Calling OpenAI LLM for session {state['session_id']}")

        # Build messages for LLM
        messages = [
            SystemMessage(content="You are a helpful AI assistant. Provide clear, concise, and friendly responses.")
        ]

        # Add chat history
        for msg in state["chat_history"]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        # Add current message
        messages.append(HumanMessage(content=state["message"]))

        try:
            # Call LLM
            response = self.llm.invoke(messages)
            state["response"] = response.content
            logger.info(f"Received response from OpenAI for session {state['session_id']}")

        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            state["response"] = "I apologize, but I'm having trouble processing your request right now."

        return state

    def format_response(self, state: ConversationState) -> ConversationState:
        session_id = state["session_id"]

        # Update chat history
        self.session_histories[session_id].append({
            "role": "user",
            "content": state["message"]
        })
        self.session_histories[session_id].append({
            "role": "assistant",
            "content": state["response"]
        })

        logger.info(f"Formatted response for session {session_id}")
        return state

    def process_message(self, session_id: str, message: str) -> str:
        initial_state = ConversationState(
            session_id=session_id,
            message=message,
            chat_history=[],
            response=""
        )

        logger.info(f"Processing message for session {session_id}")
        final_state = self.graph.invoke(initial_state)

        return final_state["response"]

    def clear_session(self, session_id: str):
        if session_id in self.session_histories:
            del self.session_histories[session_id]
            logger.info(f"Cleared history for session {session_id}")
