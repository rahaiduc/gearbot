from playwright.async_api import async_playwright, Page
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page: Optional[Page] = None
        self.headless = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
        self.timeout = int(os.getenv("NAVIGATION_TIMEOUT", 30000))

    async def start(self, headless: bool = None):
        """Inicia el navegador"""
        if headless is None:
            headless = self.headless

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            slow_mo=300 if not headless else 0
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(self.timeout)

    async def stop(self):
        """Cierra el navegador"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
        except Exception:
            pass
        try:
            if self.context:
                await self.context.close()
                self.context = None
        except Exception:
            pass
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception:
            pass
        if hasattr(self, 'playwright') and self.playwright:
            try:
                await self.playwright.stop()
                self.playwright = None
            except Exception:
                pass

    # ==================== Tools methods ====================

    async def navigate(self, url: str) -> dict:
        """Navega a una URL"""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        await self.page.goto(url, wait_until="domcontentloaded")
        return await self.get_current_page_info()

    async def extract_text(self, selector: str = "body") -> str:
        """Extrae el texto de un pagina"""
        return await self.page.inner_text(selector)

    async def click(self, selector: str):
        """Hace clic en un elemento"""
        await self.page.click(selector)

    async def fill(self, selector: str, value: str):
        """Rellena un campo de formulario"""
        await self.page.fill(selector, value)

    async def get_current_page_info(self) -> dict:
        """Devuelve información actual de la página"""
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "preview": (await self.page.content())[:600] + "..."
        }


# Instancia global
browser_manager = BrowserManager()