import os

from app.llm.providers.openai_compatible import OpenAICompatibleProvider


def configured_provider_names() -> list[str]:
    configured = os.getenv("LLM_PROVIDER", "none").strip().lower()
    if configured in {"", "none", "off", "false"}:
        return []
    if configured == "auto":
        names = []
        if os.getenv("OPENAI_API_KEY"):
            names.append("openai")
        if os.getenv("DEEPSEEK_API_KEY"):
            names.append("deepseek")
        if os.getenv("DOUBAO_API_KEY") or os.getenv("ARK_API_KEY"):
            names.append("doubao")
        if os.getenv("OLLAMA_BASE_URL"):
            names.append("ollama")
        return names
    return [item.strip() for item in configured.split(",") if item.strip()]


def build_provider_adapters() -> dict[str, OpenAICompatibleProvider]:
    adapters: dict[str, OpenAICompatibleProvider] = {}
    for name in configured_provider_names():
        adapter = _build_provider(name)
        if adapter is not None:
            adapters[name] = adapter
    return adapters


def configured_models_for(provider: str) -> list[str]:
    env_name = f"{provider.upper()}_MODELS"
    raw = os.getenv(env_name, "").strip()
    if raw:
        return [item.strip() for item in raw.split(",") if item.strip()]
    defaults = {
        "openai": ["gpt-4o-mini"],
        "deepseek": ["deepseek-chat", "deepseek-reasoner"],
        "doubao": [],
        "ollama": ["qwen2.5"],
    }
    return defaults.get(provider, [])


def _build_provider(provider: str) -> OpenAICompatibleProvider | None:
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        return OpenAICompatibleProvider(
            provider_name="openai",
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=api_key,
        )
    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return None
        return OpenAICompatibleProvider(
            provider_name="deepseek",
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            api_key=api_key,
        )
    if provider == "doubao":
        api_key = os.getenv("DOUBAO_API_KEY", os.getenv("ARK_API_KEY"))
        if not api_key:
            return None
        return OpenAICompatibleProvider(
            provider_name="doubao",
            base_url=os.getenv("DOUBAO_BASE_URL", os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")),
            api_key=api_key,
        )
    if provider == "ollama":
        return OpenAICompatibleProvider(
            provider_name="ollama",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1"),
            api_key=os.getenv("OLLAMA_API_KEY"),
        )
    return None
