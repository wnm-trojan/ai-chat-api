"""
Composition root: this is the ONLY place that wires concrete infrastructure
classes into the application layer's use cases. Routes depend only on these
factory functions via FastAPI's Depends().
"""
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.infrastructure.db.database import get_db_session
from app.infrastructure.repositories.sqlalchemy_conversation_repository import (
    SQLAlchemyConversationRepository,
)
from app.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.infrastructure.cache.redis_cache import RedisCacheClient
from app.infrastructure.external.openai_client import OpenAILLMClient
from app.infrastructure.security.jwt_handler import JWTHandler
from app.infrastructure.security.password_hasher import BcryptPasswordHasher
from app.application.use_cases.chat_use_case import ChatUseCase
from app.application.use_cases.auth_use_case import AuthUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Singletons that hold their own connection pools
_redis_cache = RedisCacheClient(settings.REDIS_URL)
_openai_client = OpenAILLMClient(settings.OPENAI_API_KEY)
_jwt_handler = JWTHandler(settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM, settings.JWT_EXPIRE_MINUTES)
_password_hasher = BcryptPasswordHasher()


def get_cache_client() -> RedisCacheClient:
    return _redis_cache


def get_jwt_handler() -> JWTHandler:
    return _jwt_handler


def get_auth_use_case(session: AsyncSession = Depends(get_db_session)) -> AuthUseCase:
    user_repo = SQLAlchemyUserRepository(session)
    return AuthUseCase(user_repo=user_repo, password_hasher=_password_hasher, jwt_handler=_jwt_handler)


def get_chat_use_case(session: AsyncSession = Depends(get_db_session)) -> ChatUseCase:
    conversation_repo = SQLAlchemyConversationRepository(session)
    return ChatUseCase(
        conversation_repo=conversation_repo,
        llm_client=_openai_client,
        cache_client=_redis_cache,
        cache_ttl_seconds=settings.CACHE_TTL_SECONDS,
    )


async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
) -> UUID:
    try:
        subject = jwt_handler.decode_token(token)
        return UUID(subject)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
