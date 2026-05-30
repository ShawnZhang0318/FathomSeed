import json
import urllib.error
import urllib.request
from typing import Any

from app.llm.providers.base import ChatMessage, LLMCallResult


class ProviderCallError(RuntimeError):
    pass


class OpenAICompatibleProvider:
    def __init__(
        self,
        *,
        provider_name: str,
        base_url: str,
        api_key: str | None = None,
        timeout_seconds: float = 45,
    ) -> None:
        self.provider_name = provider_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def list_models(self) -> list[str]:
        try:
            payload = self._request("GET", f"{self.base_url}/models", None)
        except ProviderCallError:
            return []
        data = payload.get("data", [])
        models: list[str] = []
        for item in data:
            model_id = item.get("id") if isinstance(item, dict) else None
            if isinstance(model_id, str):
                models.append(model_id)
        return models

    def complete(
        self,
        *,
        model: str,
        messages: list[ChatMessage],
        temperature: float = 0.3,
        response_format: str | None = None,
    ) -> LLMCallResult:
        body: dict[str, Any] = {
            "model": model,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
            "temperature": temperature,
        }
        if response_format == "json":
            body["response_format"] = {"type": "json_object"}
        payload = self._request("POST", f"{self.base_url}/chat/completions", body)
        choices = payload.get("choices", [])
        if not choices:
            raise ProviderCallError(f"{self.provider_name}:{model} returned no choices")
        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        text = message.get("content", "")
        if not isinstance(text, str) or not text.strip():
            raise ProviderCallError(f"{self.provider_name}:{model} returned empty content")
        return LLMCallResult(
            text=text,
            raw=payload,
            model=model,
            provider=self.provider_name,
        )

    def _request(self, method: str, url: str, body: dict[str, Any] | None) -> dict[str, Any]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise ProviderCallError(f"{self.provider_name} HTTP {exc.code}: {details}") from exc
        except OSError as exc:
            raise ProviderCallError(f"{self.provider_name} request failed: {exc}") from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ProviderCallError(f"{self.provider_name} returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ProviderCallError(f"{self.provider_name} returned non-object JSON")
        return payload

