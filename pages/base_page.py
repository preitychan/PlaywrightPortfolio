"""Base page with shared methods used across all page objects."""
from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str) -> None:
        self.page.goto(url)

    def click(self, locator) -> None:
        locator.click()

    def fill(self, locator, text: str) -> None:
        locator.fill(text)

    def get_text(self, locator) -> str:
        return locator.inner_text()

    def is_visible(self, locator) -> bool:
        return locator.is_visible()

    def wait_for_url(self, url_pattern: str, timeout: int = 10000) -> None:
        self.page.wait_for_url(url_pattern, timeout=timeout)

    def assert_visible(self, locator) -> None:
        expect(locator).to_be_visible()

    def assert_text(self, locator, text: str) -> None:
        expect(locator).to_have_text(text)

    def assert_url(self, url_pattern: str) -> None:
        expect(self.page).to_have_url(url_pattern)

    def take_screenshot(self, path: str) -> None:
        self.page.screenshot(path=path)

