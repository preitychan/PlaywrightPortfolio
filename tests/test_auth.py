"""Authentication tests."""
import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


class TestAuth:
    def test_successful_login(self, page, login_page: LoginPage, users):
        login_page.goto()
        login_page.login(users["standard_user"]["username"], users["standard_user"]["password"])
        page.wait_for_url("**/inventory.html")
        inventory = InventoryPage(page)
        inventory.assert_visible(inventory.inventory_list)

    def test_locked_out_user_shows_error(self, login_page: LoginPage, users):
        login_page.goto()
        login_page.login(users["locked_out_user"]["username"], users["locked_out_user"]["password"])
        assert login_page.is_error_visible()
        assert "locked out" in login_page.get_error_message().lower()

    def test_invalid_credentials_shows_error(self, login_page: LoginPage):
        login_page.goto()
        login_page.login("invalid_user", "wrong_password")
        assert login_page.is_error_visible()
        assert "username and password do not match" in login_page.get_error_message().lower()

    def test_empty_credentials_shows_error(self, login_page: LoginPage):
        login_page.goto()
        login_page.login("", "")
        assert login_page.is_error_visible()
        assert "username is required" in login_page.get_error_message().lower()

    @pytest.mark.parametrize("username", ["problem_user", "performance_glitch_user"])
    def test_other_valid_users_can_login(self, page, login_page: LoginPage, users, username):
        login_page.goto()
        login_page.login(users[username]["username"], users[username]["password"])
        page.wait_for_url("**/inventory.html")
        inventory = InventoryPage(page)
        inventory.assert_visible(inventory.inventory_list)

