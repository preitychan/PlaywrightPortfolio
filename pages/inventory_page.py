"""Inventory (e-commerce store) page locators and actions."""
from playwright.sync_api import Page
from pages.base_page import BasePage


class InventoryPage(BasePage):
    URL = "/inventory.html"

    def __init__(self, page: Page):
        super().__init__(page)
        self.inventory_list = page.locator(".inventory_list")
        self.inventory_items = page.locator(".inventory_item")
        self.cart_badge = page.locator(".shopping_cart_badge")
        self.cart_link = page.locator(".shopping_cart_link")
        self.sort_dropdown = page.locator(".product_sort_container")
        self.page_title = page.locator(".title")

    def goto(self) -> None:
        self.navigate(self.URL)

    def add_item_to_cart_by_name(self, item_name: str) -> None:
        item = self.inventory_items.filter(has_text=item_name)
        item.locator("button", has_text="Add to cart").click()

    def remove_item_from_cart_by_name(self, item_name: str) -> None:
        item = self.inventory_items.filter(has_text=item_name)
        item.locator("button", has_text="Remove").click()

    def get_cart_count(self) -> int:
        if self.cart_badge.count() == 0:
            return 0
        return int(self.cart_badge.inner_text())

    def open_cart(self) -> None:
        self.click(self.cart_link)

    def sort_by(self, option_value: str) -> None:
        self.sort_dropdown.select_option(option_value)

    def get_item_names(self) -> list:
        return self.page.locator(".inventory_item_name").all_inner_texts()

    def get_item_prices(self) -> list:
        prices = self.page.locator(".inventory_item_price").all_inner_texts()
        return [float(p.replace("$", "")) for p in prices]

