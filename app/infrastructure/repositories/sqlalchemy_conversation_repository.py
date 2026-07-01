from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.conversation import Conversation, Message, Role
from app.domain.repositories.conversation_repository import ConversationRepository
from app.infrastructure.db.models import ConversationModel, MessageModel


class SQLAlchemyConversationRepository(ConversationRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        stmt = (
            select(ConversationModel)
            .options(selectinload(ConversationModel.messages))
            .where(ConversationModel.id == conversation_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_user(self, user_id: UUID) -> list[Conversation]:
        stmt = (
            select(ConversationModel)
            .options(selectinload(ConversationModel.messages))
            .where(ConversationModel.user_id == user_id)
            .order_by(ConversationModel.updated_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, user_id: UUID, title: str) -> Conversation:
        model = ConversationModel(user_id=user_id, title=title)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def save(self, conversation: Conversation) -> None:
        stmt = (
            select(ConversationModel)
            .options(selectinload(ConversationModel.messages))
            .where(ConversationModel.id == conversation.id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one()

        existing_ids = {m.id for m in model.messages}
        for msg in conversation.messages:
            if msg.id not in existing_ids:
                model.messages.append(
                    MessageModel(
                        id=msg.id,
                        role=msg.role.value,
                        content=msg.content,
                        created_at=msg.created_at,
                    )
                )
        model.title = conversation.title
        await self._session.commit()

    @staticmethod
    def _to_entity(model: ConversationModel) -> Conversation:
        return Conversation(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            created_at=model.created_at,
            updated_at=model.updated_at,
            messages=[
                Message(id=m.id, role=Role(m.role), content=m.content, created_at=m.created_at)
                for m in model.messages
            ],
        )
