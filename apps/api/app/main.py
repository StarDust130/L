from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import require_user
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes


@app.get("/me")
def get_current_user(
    user_id: Annotated[str, Depends(require_user)],
) -> dict[str, str]:
    return {"user_id": user_id}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
