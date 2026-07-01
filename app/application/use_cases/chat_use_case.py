"""
Application layer: business workflow orchestration.
Depends only on domain ports (interfaces) — never on concrete infrastructure classes.
This is what makes the architecture "clean": you can unit-test this with fakes/mocks,
no DB, no Redis, no real OpenAI calls required.
"""
import hashlib
import json

from app.domain.entities.conversation import Role
from app.domain.repositories.cache_client import CacheClient
from app.domain.repositories.conversation_repository import ConversationRepository
from app.domain.repositories.llm_client import LLMClient
from app.application.dto.chat_dto import ChatRequestDTO, ChatResponseDTO


class ChatUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        llm_client: LLMClient,
        cache_client: CacheClient,
        cache_ttl_seconds: int = 3600,
    ):
        self._conversation_repo = conversation_repo
        self._llm_client = llm_client
        self._cache = cache_client
        self._cache_ttl = cache_ttl_seconds

    async def execute(self, request: ChatRequestDTO) -> ChatResponseDTO:
        # 1. Load or create the conversation
        if request.conversation_id:
            conversation = await self._conversation_repo.get_by_id(request.conversation_id)
            if conversation is None or conversation.user_id != request.user_id:
                raise ValueError("Conversation not found")
        else:
            conversation = await self._conversation_repo.create(
                user_id=request.user_id,
                title=request.message[:50],
            )

        # 2. Record the user's message in history
        conversation.add_message(Role.USER, request.message)

        # 3. Cache lookup — key derived from full message history + model,
        #    so identical conversational context returns a cached reply instantly.
        cache_key = self._build_cache_key(conversation.id, conversation.history_as_openai_messages(), request.model)
        cached_reply = await self._cache.get(cache_key)

        if cached_reply is not None:
            conversation.add_message(Role.ASSISTANT, cached_reply)
            await self._conversation_repo.save(conversation)
            return ChatResponseDTO(conversation_id=conversation.id, reply=cached_reply, cached=True)

        # 4. Cache miss -> call the LLM
        reply = await self._llm_client.get_completion(
            messages=conversation.history_as_openai_messages(),
            model=request.model,
        )

        # 5. Persist assistant reply + populate cache
        conversation.add_message(Role.ASSISTANT, reply)
        await self._conversation_repo.save(conversation)
        await self._cache.set(cache_key, reply, ttl_seconds=self._cache_ttl)

        return ChatResponseDTO(conversation_id=conversation.id, reply=reply, cached=False)

    @staticmethod
    def _build_cache_key(conversation_id, messages: list[dict], model: str) -> str:
        payload = json.dumps({"messages": messages, "model": model}, sort_keys=True)
        digest = hashlib.sha256(payload.encode()).hexdigest()
        return f"chat:{conversation_id}:{digest}"
