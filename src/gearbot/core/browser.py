"""Browser manager using Playwright for web automation tasks."""
from typing import Optional
from playwright.async_api import async_playwright, Page
from gearbot.config import NAVIGATION_TIMEOUT, BROWSER_HEADLESS

class BrowserManager:
    """Browser manager for handling Playwright browser instances and operations.

    Attributes:
        playwright: The Playwright instance.
        browser: The browser instance.
        context: The browser context.
        page: The current page instance.
        headless: Whether to run the browser in headless mode.
        timeout: Default navigation timeout in milliseconds.
    """
    def __init__(self):
        """Initializes the BrowserManager with default settings."""
        self.playwright = None
        self.browser = None
        self.context = None
        self.page: Optional[Page] = None
        self.headless = BROWSER_HEADLESS.lower() == "true"
        self.timeout = int(NAVIGATION_TIMEOUT)

    async def start(self, headless: bool = None):
        """Starts the browser instance.

         Args:
            headless: Optional override for headless mode. If None, uses the default configuration.
        """
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
        """Closes the browser instance and cleans up resources."""
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
        """Navigates to a specified URL and returns current page information.

        Args:
            url: The URL to navigate to.
        Returns:
            A dictionary containing the current page's URL, title, and a content preview.
        """
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        await self.page.goto(url, wait_until="domcontentloaded")
        return await self.get_current_page_info()

    async def extract_text(self, selector: str = "body") -> str:
        """Extracts text content from a specified element.

        Args:
            selector: The HTML selector for the element from which to extract text.

        Returns:
            The text content of the specified element.
        """
        return await self.page.inner_text(selector)

    async def click(self, selector: str):
        """Clicks an element specified by the selector.

        Args:
            selector: The HTML selector for the element to click.
        """
        if selector.startswith("text="):
            await self.page.get_by_text(selector[5:]).click(timeout=10000)
        else:
            await self.page.wait_for_selector(selector, timeout=10000)
            await self.page.click(selector)

    async def fill(self, selector: str, value: str):
        """Fills an input field specified by the selector with a given value.
        
        Args:
            selector: The HTML selector for the input field to fill.
            value: The value to fill the input field with.
        """
        await self.page.fill(selector, value)

    async def get_current_page_info(self) -> dict:
        """Retrieves information about the current page, including URL, title, and a 
        content preview.
        
        Returns:
            A dictionary containing the current page's URL, title, and a content preview.
        """
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "preview": (await self.page.content())[:600] + "..."
        }


# Global instance of the BrowserManager to be used across the application
browser_manager = BrowserManager()
