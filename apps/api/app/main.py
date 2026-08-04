from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import require_user
from app.config import get_settings
from app.routers.profile import router as profile_router
from app.routers.resumes import router as resumes_router

# ⚙️ App settings
settings = get_settings()

# 🚀 FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

# 🌐 CORS
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


# 🛣️ Routes
@app.get("/me")
def get_current_user(
    user_id: Annotated[str, Depends(require_user)],
) -> dict[str, str]:
    return {"user_id": user_id}


app.include_router(resumes_router)  # 📄 Resume routes
app.include_router(profile_router)  # 👤 Profile routes


# ❤️ Health check
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
