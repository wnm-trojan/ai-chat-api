from passlib.context import CryptContext

from app.application.use_cases.auth_use_case import PasswordHasherPort

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordHasher(PasswordHasherPort):
    def hash(self, plain: str) -> str:
        return _pwd_context.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return _pwd_context.verify(plain, hashed)
