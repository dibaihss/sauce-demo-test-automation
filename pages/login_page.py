"""Page Object for the SauceDemo Login page."""
from playwright.sync_api import Page, expect


class LoginPage:
    URL = "https://www.saucedemo.com"

    # --- Locators ---
    USERNAME_INPUT = "#user-name"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_MESSAGE = "[data-test='error']"

    def __init__(self, page: Page) -> None:
        self._page = page

    # --- Actions ---
    def navigate(self) -> None:
        self._page.goto(self.URL)

    def login(self, username: str, password: str) -> None:
        self._page.fill(self.USERNAME_INPUT, username)
        self._page.fill(self.PASSWORD_INPUT, password)
        self._page.click(self.LOGIN_BUTTON)

    # --- Assertions ---
    def assert_error_message(self, expected_text: str) -> None:
        expect(self._page.locator(self.ERROR_MESSAGE)).to_have_text(expected_text)

    def assert_on_products_page(self) -> None:
        self._page.wait_for_url("**/inventory.html")
        expect(self._page.locator(".title")).to_have_text("Products")
