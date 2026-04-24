"""
Tests for the SauceDemo Login functionality.

Covers:
- Successful login with standard_user
- Login with locked_out_user
- Login with wrong password
- Login with empty credentials
"""
import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage


VALID_USER = "standard_user"
VALID_PASS = "secret_sauce"
LOCKED_USER = "locked_out_user"
WRONG_PASS = "wrong_password"


@pytest.fixture(autouse=True)
def go_to_login(page: Page):
    login = LoginPage(page)
    login.navigate()
    return login


class TestLoginSuccess:
    def test_valid_credentials_redirect_to_inventory(self, page: Page) -> None:
        """standard_user with correct password lands on the Products page."""
        login = LoginPage(page)
        login.login(VALID_USER, VALID_PASS)
        login.assert_on_inventory_page()

    def test_page_title_after_login(self, page: Page) -> None:
        """Browser tab still has the SauceDemo title after login."""
        login = LoginPage(page)
        login.login(VALID_USER, VALID_PASS)
        login.assert_on_inventory_page()
        assert "Swag Labs" in page.title()


class TestLoginFailure:
    def test_locked_out_user_shows_error(self, page: Page) -> None:
        login = LoginPage(page)
        login.login(LOCKED_USER, VALID_PASS)
        login.assert_error_message(
            "Epic sadface: Sorry, this user has been locked out."
        )

    def test_wrong_password_shows_error(self, page: Page) -> None:
        login = LoginPage(page)
        login.login(VALID_USER, WRONG_PASS)
        login.assert_error_message(
            "Epic sadface: Username and password do not match any user in this service"
        )

    def test_empty_username_shows_error(self, page: Page) -> None:
        login = LoginPage(page)
        login.login("", VALID_PASS)
        login.assert_error_message("Epic sadface: Username is required")

    def test_empty_password_shows_error(self, page: Page) -> None:
        login = LoginPage(page)
        login.login(VALID_USER, "")
        login.assert_error_message("Epic sadface: Password is required")

    def test_both_empty_shows_error(self, page: Page) -> None:
        login = LoginPage(page)
        login.login("", "")
        login.assert_error_message("Epic sadface: Username is required")
