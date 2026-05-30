from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class LLMCallResult:
    text: str
    raw: dict[str, Any]
    model: str
    provider: str


class LLMProviderAdapter(Protocol):
    provider_name: str

    def list_models(self) -> list[str]:
        ...

    def complete(
        self,
        *,
        model: str,
        messages: list[ChatMessage],
        temperature: float = 0.3,
        response_format: str | None = None,
    ) -> LLMCallResult:
        ...

