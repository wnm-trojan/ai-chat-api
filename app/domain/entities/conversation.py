"""
Domain layer: Conversation + Message aggregate.
No FastAPI / SQLAlchemy / Redis imports allowed here — keep it framework-agnostic.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    role: Role
    content: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Conversation:
    id: UUID
    user_id: UUID
    title: str
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, role: Role, content: str) -> Message:
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        self.updated_at = datetime.utcnow()
        return msg

    def history_as_openai_messages(self) -> list[dict]:
        """Convert to the format OpenAI's chat.completions API expects."""
        return [{"role": m.role.value, "content": m.content} for m in self.messages]
