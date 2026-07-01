from openai import AsyncOpenAI

from app.domain.repositories.llm_client import LLMClient


class OpenAILLMClient(LLMClient):
    def __init__(self, api_key: str):
        self._client = AsyncOpenAI(api_key=api_key)

    async def get_completion(self, messages: list[dict], model: str = "gpt-4o-mini") -> str:
        response = await self._client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content
