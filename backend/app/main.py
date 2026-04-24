import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.agent import router as agent_router


def _get_allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "*").strip()
    if not raw:
        return ["*"]
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    return origins or ["*"]


app = FastAPI(title="Talent Scouting & Engagement Agent", version="0.1.0")

allowed_origins = _get_allowed_origins()
allow_credentials = allowed_origins != ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(agent_router)
