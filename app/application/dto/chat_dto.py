from dataclasses import dataclass
from uuid import UUID


@dataclass
class ChatRequestDTO:
    user_id: UUID
    conversation_id: UUID | None  # None => start a new conversation
    message: str
    model: str = "gpt-4o-mini"


@dataclass
class ChatResponseDTO:
    conversation_id: UUID
    reply: str
    cached: bool = False
