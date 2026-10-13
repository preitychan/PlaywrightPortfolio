"""End-to-end shopping cart and checkout user journey tests."""
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage, CheckoutPage


class TestShoppingCart:
    def test_add_single_item_to_cart(self, logged_in_page, inventory_page: InventoryPage):
        inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
        assert inventory_page.get_cart_count() == 1

    def test_add_multiple_items_to_cart(self, logged_in_page, inventory_page: InventoryPage):
        inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
        inventory_page.add_item_to_cart_by_name("Sauce Labs Bike Light")
        assert inventory_page.get_cart_count() == 2

    def test_remove_item_from_cart(self, logged_in_page, inventory_page: InventoryPage):
        inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
        inventory_page.remove_item_from_cart_by_name("Sauce Labs Backpack")
        assert inventory_page.get_cart_count() == 0

    def test_sort_items_price_low_to_high(self, logged_in_page, inventory_page: InventoryPage):
        inventory_page.sort_by("lohi")
        prices = inventory_page.get_item_prices()
        assert prices == sorted(prices)

    def test_complete_checkout_flow(
        self,
        logged_in_page,
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

