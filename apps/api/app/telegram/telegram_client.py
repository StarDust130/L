from typing import Any

import httpx

from app.core.config import get_settings

settings = get_settings()

import random

THINKING_MESSAGES = [
    "🤔 Thinking...",
    "🧠 Working on it...",
    "🔎 Checking...",
    "⚡ One sec...",
    "👀 Looking into it...",
    "✨ Putting it together...",
    "🚀 Almost there...",
    "🛠️ Working...",
]


async def send_typing(chat_id: str) -> int:
    """🤖 Send a random AI-style thinking message."""

    text = random.choice(THINKING_MESSAGES)

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

    return data["result"]["message_id"]


async def update_typing(
    chat_id: str,
    message_id: int,
) -> None:
    """🔄 Change the AI thinking message."""

    text = random.choice(THINKING_MESSAGES)

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/editMessageText"

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=payload,
        )

        response.raise_for_status()


async def stop_typing(
    chat_id: str,
    message_id: int,
) -> None:
    """🧹 Remove the temporary AI thinking message."""

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/deleteMessage"

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=payload,
        )

        response.raise_for_status()


async def send_message(
    chat_id: str,
    text: str,
    reply_markup: dict[str, Any] | None = None,
    parse_mode: str | None = None,
) -> None:
    """📤 Send a message through Telegram."""

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"

    payload: dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
    }

    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    if parse_mode is not None:
        payload["parse_mode"] = parse_mode

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=payload,
        )

        if not response.is_success:
            print(f"❌ Telegram API error: {response.text}")

        response.raise_for_status()
