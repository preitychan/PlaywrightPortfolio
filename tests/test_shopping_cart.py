"""End-to-end shopping cart and checkout user journey tests."""
import pytest
from playwright.sync_api import Browser, Page

from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage, CheckoutPage
from pages.login_page import LoginPage


@pytest.fixture(scope="session")
def standard_user_storage_state(browser: Browser, base_url, users, tmp_path_factory) -> str:
    """Logs in as standard_user ONCE for the whole test session and saves the
    resulting storage_state. Every test in this file reuses that saved session
    instead of repeating the login UI flow (already covered by test_auth.py)."""
    path = tmp_path_factory.mktemp("storage_state") / "standard_user.json"
    context = browser.new_context(base_url=base_url)
    page = context.new_page()

    login = LoginPage(page)
    login.goto()
    login.login(users["standard_user"]["username"], users["standard_user"]["password"])
    page.wait_for_url("**/inventory.html")

    context.storage_state(path=str(path))
    context.close()
    return str(path)


@pytest.fixture
def page(browser: Browser, base_url, standard_user_storage_state) -> Page:
    """Overrides pytest-playwright's default `page` fixture for this file only:
    each test still gets a brand-new, fully isolated context (so cart state from
    one test can never leak into another), but it starts pre-authenticated via
    the saved storage_state instead of performing a fresh UI login every time."""
    context = browser.new_context(base_url=base_url, storage_state=standard_user_storage_state)
    page = context.new_page()
    page.goto("/inventory.html")
    yield page
    context.close()


class TestShoppingCart:
    def test_add_single_item_to_cart(self, page: Page, inventory_page: InventoryPage):
        inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
        assert inventory_page.get_cart_count() == 1

    def test_add_multiple_items_to_cart(self, page: Page, inventory_page: InventoryPage):
        inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
        inventory_page.add_item_to_cart_by_name("Sauce Labs Bike Light")
        assert inventory_page.get_cart_count() == 2

    def test_remove_item_from_cart(self, page: Page, inventory_page: InventoryPage):
        inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
        inventory_page.remove_item_from_cart_by_name("Sauce Labs Backpack")
        assert inventory_page.get_cart_count() == 0

    def test_sort_items_price_low_to_high(self, page: Page, inventory_page: InventoryPage):
        inventory_page.sort_by("lohi")
        prices = inventory_page.get_item_prices()
        assert prices == sorted(prices)

    def test_complete_checkout_flow(
        self,
        page: Page,
        inventory_page: InventoryPage,
        cart_page: CartPage,
        checkout_page: CheckoutPage,
    ):

        inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
        inventory_page.add_item_to_cart_by_name("Sauce Labs Bike Light")
        inventory_page.open_cart()

        item_names = cart_page.get_cart_item_names()
        assert "Sauce Labs Backpack" in item_names
        assert "Sauce Labs Bike Light" in item_names

        cart_page.checkout()
        checkout_page.fill_checkout_info("John", "Doe", "12345")
        checkout_page.finish_checkout()

        assert "thank you" in checkout_page.get_complete_message().lower()

