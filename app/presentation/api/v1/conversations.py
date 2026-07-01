from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import get_db_session
from app.infrastructure.repositories.sqlalchemy_conversation_repository import (
    SQLAlchemyConversationRepository,
)
from app.presentation.dependencies import get_current_user_id

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.get("")
async def list_conversations(
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    repo = SQLAlchemyConversationRepository(session)
    conversations = await repo.list_by_user(user_id)
    return [
        {"id": c.id, "title": c.title, "updated_at": c.updated_at, "message_count": len(c.messages)}
        for c in conversations
    ]


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
):
    repo = SQLAlchemyConversationRepository(session)
    conversation = await repo.get_by_id(conversation_id)
    if conversation is None or conversation.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return {
        "id": conversation.id,
        "title": conversation.title,
        "messages": [
            {"role": m.role.value, "content": m.content, "created_at": m.created_at}
            for m in conversation.messages
        ],
    }
