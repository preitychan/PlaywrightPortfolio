"""Shopping cart and checkout page locators and actions."""
from playwright.sync_api import Page
from pages.base_page import BasePage


class CartPage(BasePage):
    URL = "/cart.html"

    def __init__(self, page: Page):
        super().__init__(page)
        self.cart_items = page.locator(".cart_item")
        self.checkout_button = page.locator("#checkout")
        self.continue_shopping_button = page.locator("#continue-shopping")

    def goto(self) -> None:
        self.navigate(self.URL)

    def get_cart_item_names(self) -> list:
        return self.page.locator(".inventory_item_name").all_inner_texts()

    def checkout(self) -> None:
        self.click(self.checkout_button)


class CheckoutPage(BasePage):
    URL = "/checkout-step-one.html"

    def __init__(self, page: Page):
        super().__init__(page)
        self.first_name_input = page.locator("#first-name")
        self.last_name_input = page.locator("#last-name")
        self.postal_code_input = page.locator("#postal-code")
        self.continue_button = page.locator("#continue")
        self.finish_button = page.locator("#finish")
        self.complete_header = page.locator(".complete-header")

    def fill_checkout_info(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.fill(self.first_name_input, first_name)
        self.fill(self.last_name_input, last_name)
        self.fill(self.postal_code_input, postal_code)
        self.click(self.continue_button)

    def finish_checkout(self) -> None:
        self.click(self.finish_button)

    def get_complete_message(self) -> str:
        return self.get_text(self.complete_header)

