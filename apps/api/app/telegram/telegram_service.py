import secrets  # 🔐 Generate secure random codes
from datetime import UTC, datetime, timedelta  # 🕐 Work with time
from html import escape  # 🛡️ Safely display HTML text

from sqlalchemy import select  # 🔎 Build database queries
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 Async database session

from app.agent.agent import run_agent
from app.agent.tools.jobs import JobRecommendation  # 💼 Job recommendation type
from app.core.config import get_settings  # ⚙️ Load app settings
from app.telegram.telegram_account_model import (
    TelegramAccount,
)  # 📱 Telegram account model
from app.telegram.telegram_client import (
    send_message,
    send_typing,  # 📤 Send Telegram message
)

# ⚙️ Load application settings
settings = get_settings()

# ⏳ OTP is valid for 10 minutes
OTP_MINUTES = 10


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
    if account.link_code_expires_at is None or account.link_code_expires_at < now:
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
    await send_connection_welcome(chat_id)


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


# 💬 Handle a normal Telegram message
async def handle_chat_message(
    db: AsyncSession,
    chat_id: str,
    message: str,
) -> None:
    # 🔎 Find connected account
    result = await db.execute(
        select(TelegramAccount).where(
            TelegramAccount.telegram_chat_id == chat_id,
        )
    )

    # 📦 Get account
    account = result.scalar_one_or_none()

    # 🚫 User is not connected
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

    # ⌨️ Show typing
    await send_typing(chat_id)

    # 🤖 Ask AI
    response = await run_agent(
        message=message,
        user_id=account.clerk_user_id,
        db=db,
    )

    # 💼 Send job recommendations
    if response.type == "jobs" and response.jobs:
        await send_job_cards(
            chat_id=chat_id,
            jobs=response.jobs,
        )
        return

    # 📤 Send normal AI response
    await send_message(
        chat_id=chat_id,
        text=response.content,
    )


# 📥 Handle every incoming Telegram message
async def handle_telegram_message(
    db: AsyncSession,
    chat_id: str,
    message: str,
) -> None:
    # 🧹 Clean the message
    message = message.strip()

    # 👋 Handle /start
    if message.lower() == "/start":
        await handle_start(
            db=db,
            chat_id=chat_id,
        )
        return

    # 🔐 Handle 8-digit link code
    if message.isdigit() and len(message) == 8:
        await handle_link_code(
            db=db,
            chat_id=chat_id,
            code=message,
        )
        return

    # 💬 Handle normal chat message
    await handle_chat_message(
        db=db,
        chat_id=chat_id,
        message=message,
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
            reply_markup=keyboard,
            parse_mode="HTML",
        )
