# Playwright Portfolio

End-to-end test automation portfolio project built with **Playwright** and **Pytest**, using the Page Object Model (POM) design pattern. Tests target the [Sauce Demo](https://www.saucedemo.com) e-commerce site.

## 📂 Project Structure

```
├── .github/workflows/playwright.yml   # CI pipeline (GitHub Actions)
├── pages/                             # Page Object Models
│   ├── base_page.py                   # Shared actions/assertions
│   ├── login_page.py                  # Login page
│   ├── inventory_page.py              # Product listing page
│   └── cart_page.py                   # Cart & checkout pages
├── tests/                             # Test suites
│   ├── conftest.py                    # Fixtures (login state, page objects, test data)
│   ├── test_auth.py                   # Authentication tests
│   └── test_shopping_cart.py          # Shopping cart / checkout journey tests
├── data/users.json                    # Test user credentials
├── pytest.ini                         # Pytest configuration
├── requirements.txt                   # Python dependencies
└── README.md
```

## 🚀 Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

## ▶️ Running Tests

Run the full suite:
```bash
pytest
```

Run a specific test file:
```bash
pytest tests/test_auth.py
```

Run in headed mode with a specific browser:
```bash
pytest --headed --browser firefox
```

Run with HTML/trace artifacts on failure (already configured in `pytest.ini`):
```bash
pytest --tracing retain-on-failure
```

View a recorded trace:
```bash
playwright show-trace test-results/<trace-folder>/trace.zip
```

## 🧪 Test Coverage

- **Authentication** (`test_auth.py`): successful login, locked-out user, invalid credentials, empty fields, multiple valid user types.
- **Shopping Cart** (`test_shopping_cart.py`): add/remove items, cart badge count, sorting, full checkout flow.

## ⚙️ CI/CD

GitHub Actions workflow (`.github/workflows/playwright.yml`) runs the full test suite on every push/PR to `main`/`master`, installs Chromium, and uploads the Playwright report/trace as build artifacts.

## 🧰 Tech Stack

- [Playwright for Python](https://playwright.dev/python/)
- [Pytest](https://docs.pytest.org/)
- [pytest-playwright](https://github.com/microsoft/playwright-pytest)

