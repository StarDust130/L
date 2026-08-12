from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.auth import require_user
from app.core.config import get_settings
from app.core.logger import setup_logging
from app.db.db import init_db
from app.job.job_router import router as job_router
from app.profile.profile_router import router as profile_router
from app.resume.resume_router import router as resumes_router
from app.telegram.telegram_router import router as telegram_router

# ⚙️ App settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🏗️ Prepare local database tables
    await init_db()

    yield


# 🚀 FastAPI app
app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

# 🌐 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.web_app_url,
        "http://localhost:3000",
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
app.include_router(job_router)  # 👙 Job routes
app.include_router(telegram_router)  # 💬 Telegram routes


# ❤️ Health check
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Logger 🪵
setup_logging()
