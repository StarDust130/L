import logging
import re
import secrets  # 🔐 Generate secure random codes
from datetime import UTC, datetime, timedelta  # 🕐 Work with time
from html import escape  # 🛡️ Safely display HTML text

from sqlalchemy import select  # 🔎 Build database queries
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 Async database session

from app.agent.agent import run_agent
from app.agent.tools.jobs import JobRecommendation  # 💼 Job recommendation type
from app.agent.types import AgentResult
from app.core.config import get_settings  # ⚙️ Load app settings
from app.profile.profile_model import CandidateProfileRecord
from app.telegram.telegram_account_model import (
    TelegramAccount,
)  # 📱 Telegram account model
from app.telegram.telegram_client import (
    send_message,
    send_typing,  # 📤 Send Telegram message
)

# ⚙️ Load application settings
settings = get_settings()
logger = logging.getLogger(__name__)

# ⏳ OTP is valid for 10 minutes
OTP_MINUTES = 10


#! 📥 (MAIN = OG) Handle every incoming Telegram message
async def handle_telegram_message(
    db: AsyncSession,
    chat_id: str,
    message: str,
) -> None:
    # 1️⃣) 🧹 Clean the message
    message = message.strip()

    # 2️⃣) 👋 Handle /start
    if message.lower() == "/start":
        await handle_start(
            db=db,
            chat_id=chat_id,
        )
        return

    # 3️⃣) 🔐 Handle 8-digit link code
    if message.isdigit() and len(message) == 8:
        await handle_link_code(
            db=db,
            chat_id=chat_id,
            code=message,
        )
        return

    # 4️⃣) 💬 Handle normal chat message
    await handle_chat_message(
        db=db,
        chat_id=chat_id,
        message=message,
    )


# 💬 (User <-> Agent) Handle a normal Telegram message
async def handle_chat_message(
    db: AsyncSession,
    chat_id: str,
    message: str,
) -> None:
    # 1️⃣) 🔎 Find connected account
    result = await db.execute(
        select(TelegramAccount).where(
            TelegramAccount.telegram_chat_id == chat_id,
        )
    )

    # 2️⃣) 📦 Get account
    account = result.scalar_one_or_none()

    # 3️⃣) 🚫 User is not connected
    if account is None:
        await send_message(
            chat_id=chat_id,
            text=(
                "🔐 <b>Please connect your L account first.</b>\n\n"
                "Open L, log in, and connect Telegram "
                "from your dashboard."
            ),
            parse_mode="HTML",
        )
        return

    await _merge_user_preferences(
        db=db,
        clerk_user_id=account.clerk_user_id,
        message=message,
    )

    # 4️⃣) ⌨️ Show typing
    await send_typing(chat_id)

    # 5️⃣) 🤖 Ask AI
    try:
        response = await run_agent(
            message=message,
            user_id=account.clerk_user_id,
            db=db,
        )
    except Exception:
        logger.exception("Telegram chat agent execution failed")
        await send_message(
            chat_id=chat_id,
            text=(
                "I hit a temporary issue while processing that request. 😭 "
                "Please try again in a moment."
            ),
        )
        return

    if isinstance(response, str):
        response = AgentResult(type="text", content=response)
    elif not isinstance(response, AgentResult):
        response = AgentResult(
            type="text",
            content=str(response),
        )

    # 6️⃣) 💼 Send job recommendations
    jobs = getattr(response, "jobs", None) or []
    if response.type == "jobs" and jobs:
        await send_job_cards(
            chat_id=chat_id,
            jobs=jobs,
        )
        return

    # 7️⃣) 📤 Send normal AI response
    await send_message(
        chat_id=chat_id,
        text=getattr(response, "content", str(response)),
    )



# ?================================ Telegram OTP Handle============================
# ?================================================================================

def _ensure_utc(value: datetime | None) -> datetime | None:
    """Normalize stored SQLite datetimes to timezone-aware UTC values."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


# 🔑 Create a OTP code to connect Telegram
async def create_link_code(
    db: AsyncSession,
    clerk_user_id: str,
) -> dict:
    # 🔎 Find the user's Telegram account
    result = await db.execute(
        select(TelegramAccount).where(
            TelegramAccount.clerk_user_id == clerk_user_id,
        )
    )

    # 📦 Get the account or None
    account = result.scalar_one_or_none()

    # ✅ Account is already connected
    if account and account.telegram_chat_id:
        return {
            "connected": True,
            "code": None,
            "expires_in": None,
        }

    # 🔢 Generate an 8-digit temporary code
    code = f"{secrets.randbelow(100_000_000):08d}"

    # ⏳ Set code expiration time
    expires_at = datetime.now(UTC) + timedelta(
        minutes=OTP_MINUTES,
    )

    # ➕ Create Telegram account if needed
    if account is None:
        account = TelegramAccount(
            clerk_user_id=clerk_user_id,
            link_code=code,
            link_code_expires_at=expires_at,
        )

        db.add(account)

    else:
        # 🔄 Replace the old code
        account.link_code = code
        account.link_code_expires_at = expires_at

    # 💾 Save the code
    await db.commit()

    # 📤 Return the temporary code
    return {
        "connected": False,
        "code": code,
        "expires_in": OTP_MINUTES * 60,
    }


# 🔐 Verify the code and connect Telegram to the user
async def verify_link_code(
    db: AsyncSession,
    telegram_chat_id: str,
    code: str,
) -> bool:
    # 🕐 Get the current UTC time
    now = datetime.now(UTC)

    # 🔎 Find the account using the code
    result = await db.execute(
        select(TelegramAccount).where(
            TelegramAccount.link_code == code,
        )
    )

    # 📦 Get the account or None
    account = result.scalar_one_or_none()

    # ❌ Code does not exist
    if account is None:
        return False

    # ⏳ Code is missing or expired
    expires_at = _ensure_utc(account.link_code_expires_at)
    if expires_at is None or expires_at < now:
        return False

    # 🔎 Check if this Telegram account is already connected
    result = await db.execute(
        select(TelegramAccount).where(
            TelegramAccount.telegram_chat_id == telegram_chat_id,
        )
    )

    # 📦 Get existing Telegram connection
    existing_account = result.scalar_one_or_none()

    # 🔎 Check if this Telegram account belongs to the same L account
    if existing_account:
        return existing_account.id == account.id

    # 🔗 Connect Telegram to the L account
    account.telegram_chat_id = telegram_chat_id

    # 🧹 Remove the temporary code
    account.link_code = None
    account.link_code_expires_at = None

    # 💾 Save the connection
    await db.commit()

    # ✅ Connection successful
    return True


# 🔐 Handle the Telegram account link code
async def handle_link_code(
    db: AsyncSession,
    chat_id: str,
    code: str,
) -> None:
    # 🔎 Verify the code
    verified = await verify_link_code(
        db=db,
        telegram_chat_id=chat_id,
        code=code,
    )

    # ✅ Code is valid
    if verified:
        await send_message(
            chat_id=chat_id,
            text=(
                "✅ <b>Telegram connected!</b>\n\n"
                "You're all set. 🤖\n"
                "You can now chat with L here."
            ),
            parse_mode="HTML",
        )
        return

    # ❌ Code is invalid
    await send_message(
        chat_id=chat_id,
        text=(
            "❌ <b>Invalid or expired code.</b>\n\n"
            "Go to your L dashboard and "
            "generate a new code."
        ),
        parse_mode="HTML",
    )


# ?================================ User Perfernces  ==============================
# ?================================================================================

def _extract_user_preferences(message: str) -> list[str]:
    """Turn natural-language preferences into a simple candidate preference list."""
    phrases: list[str] = []
    text = re.sub(r"\s+", " ", message.strip())
    candidates = re.split(
        r"[,;]|\band\b|\bbut\b|\bprefer\b|\bwant\b", text, flags=re.IGNORECASE
    )

    for candidate in candidates:
        cleaned = candidate.strip(" \t\n-\u2022*#")
        if len(cleaned) < 3:
            continue
        lowered = cleaned.lower()
        if any(
            keyword in lowered
            for keyword in (
                "remote",
                "hybrid",
                "onsite",
                "startup",
                "ai",
                "frontend",
                "backend",
                "internship",
                "full stack",
                "product",
                "data",
                "security",
                "ml",
            )
        ):
            phrases.append(cleaned)

    seen: set[str] = set()
    ordered: list[str] = []
    for phrase in phrases:
        key = phrase.lower()
        if key not in seen:
            seen.add(key)
            ordered.append(phrase)
    return ordered


async def _merge_user_preferences(
    db: AsyncSession,
    clerk_user_id: str,
    message: str,
) -> None:
    preferences = _extract_user_preferences(message)
    if not preferences:
        return

    result = await db.execute(
        select(CandidateProfileRecord).where(
            CandidateProfileRecord.clerk_user_id == clerk_user_id,
        )
    )
    record = result.scalar_one_or_none()
    if record is None:
        record = CandidateProfileRecord(
            clerk_user_id=clerk_user_id,
            profile={
                "full_name": None,
                "target_roles": [],
                "skills": [],
                "experience": [],
                "education": [],
                "locations": [],
                "preferences": preferences,
                "remote_preference": "unknown",
                "years_of_experience": None,
                "work_authorization": None,
                "links": [],
            },
        )
        db.add(record)
        await db.commit()
        return

    profile = record.profile or {}
    existing = [
        str(item).strip()
        for item in profile.get("preferences", [])
        if str(item).strip()
    ]
    merged = existing + [pref for pref in preferences if pref not in existing]
    profile["preferences"] = merged
    record.profile = profile
    await db.commit()


# ? ================================ Telegram UI Cards==============================
# ? ================================================================================

# 👋 Handle the Telegram /start command
async def handle_start(
    db: AsyncSession,
    chat_id: str,
) -> None:
    # 🔎 Find connected account
    result = await db.execute(
        select(TelegramAccount).where(
            TelegramAccount.telegram_chat_id == chat_id,
        )
    )

    # 📦 Get account
    account = result.scalar_one_or_none()

    # ✅ Show connected user menu
    if account:
        await send_connected_welcome(chat_id)
        return

    # 🔐 Show connection instructions
    await send_connected_welcome(chat_id)


# 👋 Send welcome message to connected user
async def send_connected_welcome(
    chat_id: str,
) -> None:
    # 🎛️ Create dashboard buttons
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "💼 My Jobs",
                    "url": f"{settings.web_app_url}/dashboard",
                },
                {
                    "text": "🔎 Find Jobs",
                    "url": f"{settings.web_app_url}/dashboard",
                },
            ],
            [
                {
                    "text": "📄 Resume",
                    "url": f"{settings.web_app_url}/dashboard",
                },
            ],
        ]
    }

    # 📤 Send welcome message
    await send_message(
        chat_id=chat_id,
        text=(
            "👋 <b>Welcome back to L!</b>\n\n"
            "Your personal career intelligence assistant. 🤖\n\n"
            "<b>What can I help with?</b>\n\n"
            "💼 <b>Find jobs</b>\n"
            "Find roles that match your skills and goals.\n\n"
            "🎯 <b>Match jobs</b>\n"
            "Show the best jobs for your profile.\n\n"
            "📄 <b>Resume help</b>\n"
            "Improve your resume and find skill gaps.\n\n"
            "🧠 <b>Career guidance</b>\n"
            "Skills, interviews, salary and career paths.\n\n"
            "Just tell me what you need. 🚀"
        ),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


# 💼 Send job recommendations with Apply buttons
async def send_job_cards(
    chat_id: str,
    jobs: list[JobRecommendation],
) -> None:
    # 🔄 Send each job separately
    for job in jobs:
        # 🛡️ Safely escape job information for HTML
        location = escape(job["location"] or "Remote / Not specified")
        salary = escape(job["salary"] or "Not specified")

        # 🔘 Create Apply button
        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "🚀 Apply",
                        "url": job["apply_url"],
                    },
                ],
            ]
        }

        # 📝 Build the job message
        text = (
            f"💼 <b>{escape(job['title'])}</b>\n\n"
            f"🏢 {escape(job['company'])}\n"
            f"📍 {location}\n"
            f"💰 {salary}\n"
            f"🎯 <b>{job['match_score']:.0f}% match</b>"
        )

        # 📤 Send the job card to Telegram
        await send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard if job["apply_url"] else None,
            parse_mode="HTML",
        )
