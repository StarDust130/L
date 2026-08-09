import logging

import httpx

# 🌐 RemoteOK API endpoint
REMOTEOK_URL = "https://remoteok.com/api"

# ⏱️ Wait max 10 seconds for response
REQUEST_TIMEOUT = 10.0

# 🔄 Try 3 times before giving up
MAX_RETRIES = 3

# 📝 Logger to record what's happening
logger = logging.getLogger(__name__)


# ⚠️ Custom error when RemoteOK fails
class RemoteOKError(Exception):
    """Raised when RemoteOK cannot be reached or returns invalid data."""


# 🚀 Main function - fetch jobs with retry power!
async def remoteok_job_collector() -> list[dict]:
    """Fetch jobs from RemoteOK with retries."""

    # 🔁 Try up to 3 times
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # 📢 Log: "Starting attempt X"
            logger.info(
                "remoteok_request_started attempt=%s",
                attempt,
            )

            # 🌐 Create HTTP client with headers
            async with httpx.AsyncClient(
                timeout=REQUEST_TIMEOUT,
                headers={
                    "User-Agent": "L-Career-Intelligence/1.0",  # 🏷️ Identify ourselves
                    "Accept": "application/json",  # 📨 Want JSON back
                },
            ) as client:
                # 🎣 Get jobs from API
                response = await client.get(REMOTEOK_URL)

                # ❌ Raise error if status code is bad
                response.raise_for_status()

                # 📦 Convert response to Python data
                data = response.json()

            # 🛡️ Check if data is actually a list
            if not isinstance(data, list):
                raise RemoteOKError("RemoteOK returned invalid data")

            # ✅ Success! Log how many jobs found
            logger.info(
                "remoteok_request_completed jobs=%s",
                len(data) - 1,
            )

            # 📋 First item is metadata; remaining items are jobs ← Skip first!
            return data[1:]

        # 🚨 Catch network or API errors
        except (httpx.HTTPError, RemoteOKError) as exc:
            # ⚠️ Log the error but keep trying
            logger.warning(
                "remoteok_request_failed attempt=%s error=%s",
                attempt,
                exc,
            )

            # 💥 Out of retries? Give up!
            if attempt == MAX_RETRIES:
                logger.error("remoteok_request_exhausted_retries")

                raise RemoteOKError("RemoteOK request failed after retries") from exc

    # 🛡️ Should never be reached - safety net
    raise RemoteOKError("RemoteOK collection failed")
