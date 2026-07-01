# AI Chat API — Clean Architecture

FastAPI + OpenAI + JWT auth + Redis caching + Postgres, structured in four layers
so business logic never depends on frameworks or infrastructure.

## Layers

```
app/
├── domain/            # Entities + repository/client interfaces (ports). Zero framework imports.
│   ├── entities/       (User, Conversation, Message)
│   └── repositories/    (ConversationRepository, UserRepository, LLMClient, CacheClient — all ABCs)
│
├── application/       # Use cases: business workflows. Depend only on domain ports.
│   ├── use_cases/       (ChatUseCase, AuthUseCase)
│   └── dto/
│
├── infrastructure/    # Concrete adapters implementing the ports.
│   ├── db/              (SQLAlchemy engine, ORM models)
│   ├── repositories/    (SQLAlchemy implementations of the ports)
│   ├── cache/            (Redis implementation of CacheClient)
│   ├── external/         (OpenAI implementation of LLMClient)
│   └── security/         (JWT + bcrypt implementations)
│
└── presentation/      # FastAPI: routes, schemas, DI wiring (composition root).
    ├── api/v1/          (auth.py, chat.py, conversations.py)
    ├── dependencies.py  (wires infrastructure into use cases — the only "impure" file)
    └── schemas.py
```

**Dependency rule:** arrows only point inward. `presentation` → `application` → `domain`.
`infrastructure` implements `domain` interfaces but is only *wired in* at
`presentation/dependencies.py`. This means:
- You can unit-test `ChatUseCase` with in-memory fakes, no DB/Redis/OpenAI needed.
- Swapping Postgres for Mongo, or OpenAI for Anthropic, touches only `infrastructure/`.

## How caching works

`ChatUseCase` hashes the full message history + model into a cache key before calling
OpenAI. Identical conversational context returns the cached reply (`cached: true` in
the response) instead of hitting the LLM again — cutting cost and latency for repeated
or retried prompts.

## Run it

```bash
cp .env.example .env        # fill in OPENAI_API_KEY and a real JWT_SECRET_KEY
docker compose up --build
```

API available at `http://localhost:8000`, interactive docs at `/docs`.

## Example flow

```bash
# Register
curl -X POST localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com","password":"supersecret1"}'
# -> {"access_token": "...", "token_type": "bearer"}

# Chat (start new conversation)
curl -X POST localhost:8000/api/v1/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello!"}'
# -> {"conversation_id": "...", "reply": "...", "cached": false}

# Continue the same conversation
curl -X POST localhost:8000/api/v1/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message":"What did I just say?","conversation_id":"<id from above>"}'

# List conversation history
curl localhost:8000/api/v1/conversations -H "Authorization: Bearer <token>"
```

## Notes for production

- Replace the `lifespan` auto-`create_all` with Alembic migrations.
- Rotate `JWT_SECRET_KEY` via a secrets manager, not `.env` in the image.
- Add rate limiting (e.g. `slowapi`) in front of `/chat` since it's the expensive route.
- Consider streaming responses (`chat.completions.create(stream=True)`) for better UX on long replies.
