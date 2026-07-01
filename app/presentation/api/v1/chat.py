from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dto.chat_dto import ChatRequestDTO
from app.application.use_cases.chat_use_case import ChatUseCase
from app.config import settings
from app.presentation.dependencies import get_chat_use_case, get_current_user_id
from app.presentation.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    user_id: UUID = Depends(get_current_user_id),
    use_case: ChatUseCase = Depends(get_chat_use_case),
):
    request = ChatRequestDTO(
        user_id=user_id,
        conversation_id=body.conversation_id,
        message=body.message,
        model=body.model or settings.OPENAI_DEFAULT_MODEL,
    )
    try:
        result = await use_case.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return ChatResponse(conversation_id=result.conversation_id, reply=result.reply, cached=result.cached)
