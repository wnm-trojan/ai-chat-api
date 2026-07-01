from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.application.use_cases.auth_use_case import JWTHandlerPort


class JWTHandler(JWTHandlerPort):
    def __init__(self, secret_key: str, algorithm: str, expire_minutes: int):
        self._secret = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def create_access_token(self, subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._expire_minutes)
        payload = {"sub": subject, "exp": expire}
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_token(self, token: str) -> str:
        """Returns the subject (user id) or raises ValueError if invalid/expired."""
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            subject: str | None = payload.get("sub")
            if subject is None:
                raise ValueError("Token missing subject")
            return subject
        except JWTError as e:
            raise ValueError("Invalid or expired token") from e
