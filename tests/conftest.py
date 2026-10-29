"""Pytest fixtures: setup/teardown, test data loading, authenticated state."""
import json
import os
import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage, CheckoutPage

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


@pytest.fixture(scope="session")
def users():
    """Load test user credentials from data/users.json."""
    with open(os.path.join(DATA_DIR, "users.json")) as f:
        return json.load(f)


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def inventory_page(page: Page) -> InventoryPage:
    return InventoryPage(page)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


@pytest.fixture
def checkout_page(page: Page) -> CheckoutPage:
    return CheckoutPage(page)



