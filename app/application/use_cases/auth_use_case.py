from dataclasses import dataclass

from app.domain.repositories.user_repository import UserRepository


@dataclass
class TokenPairDTO:
    access_token: str
    token_type: str = "bearer"


class PasswordHasherPort:
    """Kept minimal on purpose — implemented in infrastructure/security."""
    def hash(self, plain: str) -> str: ...
    def verify(self, plain: str, hashed: str) -> bool: ...


class JWTHandlerPort:
    def create_access_token(self, subject: str) -> str: ...


class AuthUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        password_hasher: PasswordHasherPort,
        jwt_handler: JWTHandlerPort,
    ):
        self._user_repo = user_repo
        self._hasher = password_hasher
        self._jwt = jwt_handler

    async def register(self, email: str, password: str) -> TokenPairDTO:
        existing = await self._user_repo.get_by_email(email)
        if existing:
            raise ValueError("User already exists")
        hashed = self._hasher.hash(password)
        user = await self._user_repo.create(email=email, hashed_password=hashed)
        token = self._jwt.create_access_token(subject=str(user.id))
        return TokenPairDTO(access_token=token)

    async def login(self, email: str, password: str) -> TokenPairDTO:
        user = await self._user_repo.get_by_email(email)
        if not user or not self._hasher.verify(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        token = self._jwt.create_access_token(subject=str(user.id))
        return TokenPairDTO(access_token=token)
