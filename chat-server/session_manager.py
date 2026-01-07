import uuid
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ChatSession:
    session_id: str
    created_at: str
    messages: List[Message] = field(default_factory=list)

    def add_message(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ChatSession(
            session_id=session_id,
            created_at=datetime.now().isoformat()
        )
        return session_id

    def get_session(self, session_id: str) -> ChatSession:
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.sessions[session_id]

    def get_all_sessions(self) -> List[Dict]:
        return [
            {
                "session_id": session.session_id,
                "created_at": session.created_at,
                "message_count": len(session.messages)
            }
            for session in self.sessions.values()
        ]

    def add_message(self, session_id: str, role: str, content: str):
        session = self.get_session(session_id)
        session.add_message(role, content)

    def get_messages(self, session_id: str) -> List[Dict]:
        session = self.get_session(session_id)
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in session.messages
        ]
