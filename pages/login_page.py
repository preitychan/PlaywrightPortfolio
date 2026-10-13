"""Login page locators and actions."""
from playwright.sync_api import Page
from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "/"

    def __init__(self, page: Page):
        super().__init__(page)
        self.username_input = page.locator("#user-name")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("#login-button")
        self.error_message = page.locator("[data-test='error']")

    def goto(self) -> None:
        self.navigate(self.URL)

    def login(self, username: str, password: str) -> None:
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)

    def get_error_message(self) -> str:
        return self.get_text(self.error_message)

    def is_error_visible(self) -> bool:
        return self.is_visible(self.error_message)

