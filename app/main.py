from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.infrastructure.db.database import Base, engine
from app.presentation.api.v1 import auth, chat, conversations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev convenience: auto-create tables. Use Alembic migrations in production.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(conversations.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
