import httpx


async def fetch_page(url: str) -> str:
    """🌐 Fetch readable text from a webpage."""

    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={
                "User-Agent": "L-Agent/1.0",
            },
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

        return response.text[:20_000]

    except httpx.HTTPError as exc:
        return f"Failed to fetch page: {exc}"
