import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.llm.providers import build_provider_adapters, configured_models_for


LEVEL_SCORES = {
    "none": 0.0,
    "low": 0.25,
    "medium": 0.55,
    "high": 0.82,
    "very_high": 1.0,
}


@dataclass(frozen=True)
class ModelProfile:
    id: str
    provider: str
    model: str
    display_name: str
    capabilities: dict[str, Any] = field(default_factory=dict)
    task_quality: dict[str, float] = field(default_factory=dict)
    cost_level: str = "medium"
    latency_level: str = "medium"
    reliability: float = 0.7
    verified: bool = False
    source: str = "profile"

    def capability_score(self, name: str) -> float:
        value = self.capabilities.get(name)
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)):
            return max(0.0, min(1.0, float(value)))
        if isinstance(value, str):
            return LEVEL_SCORES.get(value, 0.0)
        return 0.0

    def supports(self, name: str) -> bool:
        return self.capability_score(name) > 0.0


class ModelRegistry:
    def __init__(self, profile_path: Path | None = None) -> None:
        self.profile_path = profile_path or Path(__file__).with_name("model_profiles.json")
        self.adapters = build_provider_adapters()
        self._profiles = self._load_profiles()

    @property
    def enabled(self) -> bool:
        return bool(self.adapters)

    def providers(self) -> list[str]:
        return sorted(self.adapters)

    def list_models(self) -> list[ModelProfile]:
        if not self.enabled:
            return []
        profiles = self._configured_profiles()
        if _truthy(os.getenv("FULLMIND_LLM_DISCOVER", "false")):
            profiles = self._merge_discovered_profiles(profiles)
        return sorted(profiles, key=lambda item: (item.provider, item.model))

    def adapter_for(self, provider: str):
        return self.adapters.get(provider)

    def _configured_profiles(self) -> list[ModelProfile]:
        profiles: list[ModelProfile] = []
        for provider in self.adapters:
            configured_models = configured_models_for(provider)
            known_by_model = {
                profile.model: profile
                for profile in self._profiles
                if profile.provider == provider
            }
            for model_name in configured_models:
                profile = known_by_model.get(model_name)
                if profile is not None:
                    profiles.append(profile)
                else:
                    profiles.append(self._generic_profile(provider=provider, model=model_name, source="env"))

            if not configured_models:
                profiles.extend(profile for profile in self._profiles if profile.provider == provider)
        return profiles

    def _merge_discovered_profiles(self, profiles: list[ModelProfile]) -> list[ModelProfile]:
        by_id = {profile.id: profile for profile in profiles}
        for provider, adapter in self.adapters.items():
            for model_name in adapter.list_models():
                profile_id = f"{provider}:{model_name}"
                if profile_id not in by_id:
                    by_id[profile_id] = self._generic_profile(provider=provider, model=model_name, source="discovered")
        return list(by_id.values())

    def _load_profiles(self) -> list[ModelProfile]:
        if not self.profile_path.exists():
            return []
        raw = json.loads(self.profile_path.read_text(encoding="utf-8"))
        items = raw.get("profiles", []) if isinstance(raw, dict) else []
        profiles: list[ModelProfile] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            profiles.append(
                ModelProfile(
                    id=str(item["id"]),
                    provider=str(item["provider"]),
                    model=str(item["model"]),
                    display_name=str(item.get("display_name") or item["model"]),
                    capabilities=dict(item.get("capabilities") or {}),
                    task_quality={key: float(value) for key, value in dict(item.get("task_quality") or {}).items()},
                    cost_level=str(item.get("cost_level", "medium")),
                    latency_level=str(item.get("latency_level", "medium")),
                    reliability=float(item.get("reliability", 0.7)),
                    verified=bool(item.get("verified", False)),
                    source="profile",
                )
            )
        return profiles

    def _generic_profile(self, provider: str, model: str, source: str) -> ModelProfile:
        image_like = any(token in model.lower() for token in ("image", "seedream", "vision-generate"))
        capabilities = {
            "text": not image_like,
            "structured_json": not image_like,
            "reasoning": "medium" if not image_like else "low",
            "code": "medium" if not image_like else "low",
            "chinese": "high" if provider in {"deepseek", "doubao", "ollama"} else "medium",
            "long_text": "medium" if not image_like else "low",
            "creativity": "medium" if not image_like else "high",
            "image_generation": image_like,
        }
        task_quality = {
            "plan_generation": 0.65,
            "exercise_generation": 0.65,
            "explanation": 0.65,
            "structured_rewrite": 0.62,
        }
        if image_like:
            task_quality = {"image_generation": 0.72, "visual_asset_generation": 0.72}
        return ModelProfile(
            id=f"{provider}:{model}",
            provider=provider,
            model=model,
            display_name=model,
            capabilities=capabilities,
            task_quality=task_quality,
            cost_level="medium",
            latency_level="medium",
            reliability=0.62,
            verified=False,
            source=source,
        )


def _truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}

