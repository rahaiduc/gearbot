from playwright.async_api import async_playwright, Page
from typing import Optional

class BrowserManager:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page: Optional[Page] = None

    async def start(self, headless: bool = False):
        from playwright.async_api import async_playwright
        p = await async_playwright().start()
        self.browser = await p.chromium.launch(headless=headless, slow_mo=500)
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = await self.context.new_page()

    async def stop(self):
        if self.browser:
            await self.browser.close()

    async def navigate(self, url: str):
        if self.page:
            await self.page.goto(url, wait_until="domcontentloaded")
            return await self.get_current_state()

    async def get_current_state(self):
        if not self.page:
            return {}
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "content_preview": (await self.page.content())[:800] + "..."
        }

browser_manager = BrowserManager()