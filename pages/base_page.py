"""Base page with shared methods used across all page objects."""
import logging
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str) -> None:
        logger.info("Navigating to %s", url)
        self.page.goto(url)

    def click(self, locator) -> None:
        logger.info("Clicking %s", locator)
        locator.click()

    def fill(self, locator, text: str) -> None:
        logger.info("Filling %s with %r", locator, text)
        locator.fill(text)

    def get_text(self, locator) -> str:
        text = locator.inner_text()
        logger.info("Read text %r from %s", text, locator)
        return text

    def is_visible(self, locator) -> bool:
        return locator.is_visible()

    def wait_for_url(self, url_pattern: str, timeout: int = 10000) -> None:
        logger.info("Waiting for URL pattern %s", url_pattern)
        self.page.wait_for_url(url_pattern, timeout=timeout)

    def assert_visible(self, locator) -> None:
        logger.info("Asserting visible: %s", locator)
        expect(locator).to_be_visible()

    def assert_text(self, locator, text: str) -> None:
        logger.info("Asserting text %r on %s", text, locator)
        expect(locator).to_have_text(text)

    def assert_url(self, url_pattern: str) -> None:
        logger.info("Asserting URL matches %s", url_pattern)
        expect(self.page).to_have_url(url_pattern)

    def take_screenshot(self, path: str) -> None:
        logger.info("Taking screenshot: %s", path)
        self.page.screenshot(path=path)

