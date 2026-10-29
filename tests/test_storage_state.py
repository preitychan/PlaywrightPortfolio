"""Demonstrates Playwright's storage_state feature: capturing and reusing
browser session data (cookies + localStorage/sessionStorage) across contexts,
without needing to repeat a login or setup flow every time.

storage_state is captured from a BrowserContext via `context.storage_state(path=...)`
and replayed into a brand-new context via `browser.new_context(storage_state=path)`.

Covered scenarios:
1. Unauthenticated redirect   -> visiting a protected page with no session bounces to login.
2. Saved-state reuse          -> logging in once, then reusing that saved session to skip login.
3. Role-based access          -> two different saved sessions (different users) produce
                                  different behaviour/content from the same app.
4. Persisted preferences      -> storage_state captures localStorage too, not just cookies,
                                  demonstrated via a to-do app that persists items client-side.
"""
import logging

import pytest
from playwright.sync_api import Browser, expect

logger = logging.getLogger(__name__)

HEROKU_LOGIN_URL = "https://the-internet.herokuapp.com/login"
HEROKU_SECURE_URL = "https://the-internet.herokuapp.com/secure"
TODO_APP_URL = "https://demo.playwright.dev/todomvc/#/"


class TestUnauthenticatedRedirect:
    """Baseline: with no storage_state at all, protected pages are unreachable."""

    def test_redirects_to_login_when_not_authenticated(self, page):
        page.goto(HEROKU_SECURE_URL)
        expect(page).to_have_url(HEROKU_LOGIN_URL)
        expect(page.locator("#flash")).to_contain_text("You must login to view the secure area!")


class TestSavedStateReuse:
    """Log in once, persist the session, then prove a brand-new context can
    reuse it to skip the login flow entirely."""

    @pytest.fixture(scope="class")
    def heroku_storage_state_path(self, browser: Browser, tmp_path_factory):
        storage_dir = tmp_path_factory.mktemp("storage_state")
        path = storage_dir / "heroku_auth.json"

        context = browser.new_context()
        page = context.new_page()
        page.goto(HEROKU_LOGIN_URL)
        page.fill("#username", "tomsmith")
        page.fill("#password", "SuperSecretPassword!")
        page.click("button[type='submit']")
        expect(page.locator("#flash")).to_contain_text("You logged into a secure area!")

        context.storage_state(path=str(path))
        logger.info("Saved authenticated storage_state to %s", path)
        context.close()
        return str(path)

    def test_reusing_saved_state_skips_login(self, browser: Browser, heroku_storage_state_path):
        context = browser.new_context(storage_state=heroku_storage_state_path)
        page = context.new_page()

        page.goto(HEROKU_SECURE_URL)  # No login step - session is already authenticated.

        expect(page).to_have_url(HEROKU_SECURE_URL)
        expect(page.locator("h2")).to_have_text("Secure Area")
        context.close()


class TestRoleBasedAccess:
    """Two different saved sessions (standard_user vs problem_user on saucedemo.com)
    behave differently even though they hit the exact same inventory page -
    the difference comes purely from which storage_state is loaded."""

    @pytest.fixture(scope="class")
    def standard_user_state(self, browser: Browser, users, tmp_path_factory):
        path = tmp_path_factory.mktemp("storage_state") / "standard_user.json"
        context = browser.new_context(base_url="https://www.saucedemo.com")
        page = context.new_page()
        page.goto("/")
        page.fill("#user-name", users["standard_user"]["username"])
        page.fill("#password", users["standard_user"]["password"])
        page.click("#login-button")
        page.wait_for_url("**/inventory.html")
        context.storage_state(path=str(path))
        context.close()
        return str(path)

    @pytest.fixture(scope="class")
    def problem_user_state(self, browser: Browser, users, tmp_path_factory):
        path = tmp_path_factory.mktemp("storage_state") / "problem_user.json"
        context = browser.new_context(base_url="https://www.saucedemo.com")
        page = context.new_page()
        page.goto("/")
        page.fill("#user-name", users["problem_user"]["username"])
        page.fill("#password", users["problem_user"]["password"])
        page.click("#login-button")
        page.wait_for_url("**/inventory.html")
        context.storage_state(path=str(path))
        context.close()
        return str(path)

    def test_standard_user_sees_distinct_product_images(self, browser: Browser, standard_user_state):
        context = browser.new_context(base_url="https://www.saucedemo.com", storage_state=standard_user_state)
        page = context.new_page()
        page.goto("/inventory.html")

        image_sources = page.locator(".inventory_item_img img").evaluate_all("imgs => imgs.map(i => i.src)")
        assert len(set(image_sources)) > 1, "standard_user should see distinct product images"
        context.close()

    def test_standard_user_can_add_item_to_cart(self, browser: Browser, standard_user_state):
        """Second consumer of the standard_user_state fixture - reuses the same cached
        saved session (no second login) to check a different piece of behaviour."""
        context = browser.new_context(base_url="https://www.saucedemo.com", storage_state=standard_user_state)
        page = context.new_page()
        page.goto("/inventory.html")

        page.locator(".inventory_item", has_text="Sauce Labs Backpack").locator(
            "button", has_text="Add to cart"
        ).click()

        expect(page.locator(".shopping_cart_badge")).to_have_text("1")
        context.close()

    def test_problem_user_role_has_known_image_defect(self, browser: Browser, problem_user_state):
        """problem_user is a role on saucedemo.com with a seeded bug: every product
        image resolves to the same broken image. Loading its storage_state alone
        (no re-login) reproduces the defect, proving the role/session drives behaviour."""
        context = browser.new_context(base_url="https://www.saucedemo.com", storage_state=problem_user_state)
        page = context.new_page()
        page.goto("/inventory.html")

        image_sources = page.locator(".inventory_item_img img").evaluate_all("imgs => imgs.map(i => i.src)")
        assert len(set(image_sources)) == 1, "problem_user is expected to show the same broken image for every item"
        context.close()


class TestPersistedPreferences:
    """storage_state captures more than cookies - it snapshots localStorage/sessionStorage
    too. The Playwright TodoMVC demo app stores its to-do list in localStorage, so saving
    and reusing storage_state here proves client-side preferences/data survive across contexts."""

    @pytest.fixture(scope="class")
    def todo_storage_state_path(self, browser: Browser, tmp_path_factory):
        path = tmp_path_factory.mktemp("storage_state") / "todo_prefs.json"
        context = browser.new_context()
        page = context.new_page()
        page.goto(TODO_APP_URL)
        page.locator(".new-todo").fill("Demonstrate storage_state")
        page.locator(".new-todo").press("Enter")
        expect(page.locator(".todo-list li")).to_have_count(1)

        context.storage_state(path=str(path))
        context.close()
        return str(path)

    def test_todo_persists_across_new_context(self, browser: Browser, todo_storage_state_path):
        context = browser.new_context(storage_state=todo_storage_state_path)
        page = context.new_page()
        page.goto(TODO_APP_URL)

        expect(page.locator(".todo-list li")).to_have_count(1)
        expect(page.locator(".todo-list li")).to_have_text("Demonstrate storage_state")
        context.close()

    def test_fresh_context_without_state_starts_empty(self, browser: Browser):
        """Control case: a context with no storage_state has no saved preferences at all."""
        context = browser.new_context()
        page = context.new_page()
        page.goto(TODO_APP_URL)

        expect(page.locator(".todo-list li")).to_have_count(0)
        context.close()

