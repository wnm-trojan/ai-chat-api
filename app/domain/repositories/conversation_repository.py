"""
Port (interface). Infrastructure layer provides the concrete implementation.
Application layer depends only on this abstraction — never on SQLAlchemy directly.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.conversation import Conversation


class ConversationRepository(ABC):

    @abstractmethod
    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        ...

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> list[Conversation]:
        ...

    @abstractmethod
    async def save(self, conversation: Conversation) -> None:
        ...

    @abstractmethod
    async def create(self, user_id: UUID, title: str) -> Conversation:
        ...
