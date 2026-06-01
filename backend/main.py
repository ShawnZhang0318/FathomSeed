from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import exercises, feedback, intent, llm, methods, plans, profiles, strategies, sync, tasks
from app.core.llm_provider import LLMProvider
from app.db.session import init_db


def create_app() -> FastAPI:
    app = FastAPI(
        title="FathomSeed",
        description="AI learning experience engine with a built-in fallback and optional LLM enhancement.",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(profiles.router)
    app.include_router(intent.router)
    app.include_router(llm.router)
    app.include_router(strategies.router)
    app.include_router(methods.router)
    app.include_router(plans.router)
    app.include_router(tasks.router)
    app.include_router(feedback.router)
    app.include_router(sync.router)
    app.include_router(exercises.router)

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    @app.get("/health")
    def health() -> dict[str, str | bool | int]:
        llm_state = LLMProvider().state
        return {
            "status": "ok",
            "llm_provider": llm_state.provider,
            "llm_enabled": llm_state.enabled,
            "llm_models": llm_state.models,
        }

    static_dir = Path(__file__).resolve().parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="web")

    return app


app = create_app()
