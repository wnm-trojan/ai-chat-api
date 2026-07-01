from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstraction so the application layer isn't coupled to the OpenAI SDK.
    Swapping providers (Anthropic, local model, etc.) only touches infrastructure."""

    @abstractmethod
    async def get_completion(self, messages: list[dict], model: str = "gpt-4o-mini") -> str:
        ...
