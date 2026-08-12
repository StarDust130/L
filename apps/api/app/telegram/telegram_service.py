import secrets
from datetime import UTC, datetime, timedelta
from html import escape

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.agent import run_agent
from app.agent.tools.jobs import JobRecommendation
from app.core.config import get_settings
from app.telegram.telegram_account_model import TelegramAccount
from app.telegram.telegram_client import (
    send_message,
    send_typing,
)

settings = get_settings()

OTP_MINUTES = 10


async def create_link_code(
    db: AsyncSession,
    clerk_user_id: str,
) -> dict:
    """🔑 Create a temporary Telegram connection code."""

    result = await db.execute(
        select(TelegramAccount).where(
            TelegramAccount.clerk_user_id == clerk_user_id,
        )
    )

    account = result.scalar_one_or_none()

    # ✅ Already connected.
    if account and account.telegram_chat_id:
        return {
            "connected": True,
            "code": None,
            "expires_in": None,
        }

    # 🔢 Generate an 8-digit OTP.
    code = f"{secrets.randbelow(100_000_000):08d}"

    expires_at = datetime.now(UTC) + timedelta(
        minutes=OTP_MINUTES,
    )

    if account is None:
        account = TelegramAccount(
            clerk_user_id=clerk_user_id,
            link_code=code,
            link_code_expires_at=expires_at,
        )

        db.add(account)

    else:
        # 🔄 Replace old/expired code.
        account.link_code = code
        account.link_code_expires_at = expires_at

    await db.commit()

    return {
        "connected": False,
        "code": code,
        "expires_in": OTP_MINUTES * 60,
    }


async def verify_link_code(
    db: AsyncSession,
    telegram_chat_id: str,
    code: str,
) -> bool:
    """🔐 Verify OTP and connect Telegram to the L account."""

    now = datetime.now(UTC)

    result = await db.execute(
        select(TelegramAccount).where(
            TelegramAccount.link_code == code,
        )
    )

    account = result.scalar_one_or_none()

    # ❌ Code doesn't exist.
    if account is None:
        return False

    # ⏳ Code expired.
    if account.link_code_expires_at is None or account.link_code_expires_at < now:
        return False

    # 🔎 Check whether this Telegram account belongs
    # to another L account.
    result = await db.execute(
        select(TelegramAccount).where(
            TelegramAccount.telegram_chat_id == telegram_chat_id,
        )
    )

    existing_account = result.scalar_one_or_none()

    if existing_account:
        # ✅ Same L account — already connected.
        return existing_account.id == account.id

        # 🚫 Telegram already belongs to another account.
        return False

    # 🔗 Connect Telegram.
    account.telegram_chat_id = telegram_chat_id

    # 🧹 OTP is no longer needed.
    account.link_code = None
    account.link_code_expires_at = None

    await db.commit()

    return True


async def handle_telegram_message(
    db: AsyncSession,
    chat_id: str,
    message: str,
) -> None:
    """🧠 Handle an incoming Telegram message."""

    message = message.strip()

    # 👋 Handle /start separately.
    if message.lower() == "/start":
        result = await db.execute(
            select(TelegramAccount).where(
                TelegramAccount.telegram_chat_id == chat_id,
            )
        )

        account = result.scalar_one_or_none()

        # ✅ Already connected.
        if account:
            keyboard = {
                "inline_keyboard": [
                    [
                        {
                            "text": "💼 My Jobs",
                            "callback_data": "my_jobs",
                        },
                        {
                            "text": "🔎 Find Jobs",
                            "callback_data": "find_jobs",
                        },
                    ],
                    [
                        {
                            "text": "📄 Resume",
                            "callback_data": "resume",
                        },
                    ],
                ]
            }

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

        # ❌ Not connected.
        else:
            keyboard = {
                "inline_keyboard": [
                    [
                        {
                            "text": "🌐 Open L",
                            "url": settings.web_app_url,
                        }
                    ]
                ]
            }

            await send_message(
                chat_id=chat_id,
                text=(
                    "👋 <b>Welcome to L!</b>\n\n"
                    "🔐 Connect your L account to start chatting.\n\n"
                    "1️⃣ Tap <b>Open L</b> below.\n"
                    "2️⃣ Log in or create your account.\n"
                    "3️⃣ Open your Dashboard → Connect Telegram.\n"
                    "4️⃣ Get your 8-digit code.\n"
                    "5️⃣ Send the code here.\n\n"
                    "✅ That's it! Then you can chat with L. 🤖"
                ),
                reply_markup=keyboard,
                parse_mode="HTML",
            )

        return

    # 🔐 Check whether this message is an OTP.
    if message.isdigit() and len(message) == 8:
        verified = await verify_link_code(
            db=db,
            telegram_chat_id=chat_id,
            code=message,
        )

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
        else:
            await send_message(
                chat_id=chat_id,
                text=(
                    "❌ <b>Invalid or expired code.</b>\n\n"
                    "Go to your L dashboard and "
                    "generate a new code."
                ),
                parse_mode="HTML",
            )

        return

    # 🔎 Find the Telegram account.
    result = await db.execute(
        select(TelegramAccount).where(
            TelegramAccount.telegram_chat_id == chat_id,
        )
    )

    account = result.scalar_one_or_none()

    # 🚫 Not connected.
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

    # ⌨️ Show typing while L thinks.
    await send_typing(chat_id)

    # 🤖 Send the message to L.
    response = await run_agent(
        message=message,
        user_id=account.clerk_user_id,
        db=db,
    )

    # 📤 Send the AI response back to Telegram.
    if response.type == "jobs" and response.jobs:
        await send_job_cards(
            chat_id=chat_id,
            jobs=response.jobs,
        )
        return

    await send_message(
        chat_id=chat_id,
        text=response.content,
    )


async def send_job_cards(
    chat_id: str,
    jobs: list[JobRecommendation],
) -> None:
    """Send recommendation cards with the real application URLs."""

    for job in jobs:
        location = escape(job["location"] or "Remote / Not specified")
        salary = escape(job["salary"] or "Not specified")

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

        text = (
            f"💼 <b>{escape(job['title'])}</b>\n\n"
            f"🏢 {escape(job['company'])}\n"
            f"📍 {location}\n"
            f"💰 {salary}\n"
            f"🎯 <b>{job['match_score']:.0f}% match</b>"
        )

        await send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
