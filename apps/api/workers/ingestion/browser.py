from dataclasses import dataclass

from playwright.async_api import async_playwright


@dataclass(frozen=True)
class BrowserPage:
    url: str
    html: str


class BrowserFetcher:
    def __init__(self, *, timeout_ms: int = 25_000) -> None:
        self.timeout_ms = timeout_ms

    async def fetch(self, url: str) -> BrowserPage:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page(
                    user_agent="LJobFinder/0.1 (+job discovery; contact owner)"
                )
                await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                await page.wait_for_timeout(800)
                return BrowserPage(url=page.url, html=await page.content())
            finally:
                await browser.close()
