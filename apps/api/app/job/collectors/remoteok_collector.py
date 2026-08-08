import httpx

REMOTEOK_URL = "https://remoteok.com/api"
REQUEST_TIMEOUT = 10.0


class RemoteOKError(Exception):
    """Raised when RemoteOK cannot be reached or returns invalid data."""


async def collect_jobs() -> list[dict]:
    """Fetch current jobs from RemoteOK."""

    try:
        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": "L-Career-Intelligence/1.0",
                "Accept": "application/json",
            },
        ) as client:
            # 🌐 Fetch jobs from RemoteOK.
            response = await client.get(REMOTEOK_URL)

            # 🚨 Raise an error for 4xx/5xx responses.
            response.raise_for_status()

            # 📦 Convert JSON response into Python objects.
            data = response.json()

    except httpx.HTTPError as exc:
        # ❌ Convert HTTP errors into our own application error.
        raise RemoteOKError("Failed to fetch jobs from RemoteOK") from exc

    if not isinstance(data, list):
        # 🛡️ Protect against an unexpected API response.
        raise RemoteOKError("RemoteOK returned an invalid response")

    # 📋 First item is API metadata, remaining items are jobs.
    return data[1:]
