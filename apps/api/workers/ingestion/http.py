from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class FetchedPage:
    url: str
    status_code: int
    content_type: str
    html: str


class HttpFetcher:
    def __init__(self, *, timeout: float = 20.0) -> None:
        self.timeout = timeout

    async def fetch(self, url: str, headers: dict[str, str] | None = None) -> FetchedPage:
        default_headers = {
            "User-Agent": "LJobFinder/0.1 (+job discovery; contact owner)",
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        }
        if headers:
            default_headers.update(headers)
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers=default_headers,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return FetchedPage(
                url=str(response.url),
                status_code=response.status_code,
                content_type=response.headers.get("content-type", ""),
                html=response.text,
            )
