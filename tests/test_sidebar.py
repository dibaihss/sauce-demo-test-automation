"""Tests for the shared SauceDemo sidebar menu."""
import pytest

from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.checkout_page import (
    CheckoutCompletePage,
    CheckoutStepOnePage,
    CheckoutStepTwoPage,
)
from pages.login_page import LoginPage
from pages.product_page import ProductPage


SAUCE_LABS_BACKPACK = "Sauce Labs Backpack"
CUSTOMER = {"first": "Max", "last": "Mustermann", "postal": "12345"}


def _go_to_cart(page: Page) -> CartPage:
    products = ProductPage(page)
    products.add_item_to_cart(SAUCE_LABS_BACKPACK)
    products.go_to_cart()
    return CartPage(page)


def _go_to_checkout_step_one(page: Page) -> CheckoutStepOnePage:
    cart = _go_to_cart(page)
    cart.proceed_to_checkout()
    return CheckoutStepOnePage(page)


def _go_to_checkout_step_two(page: Page) -> CheckoutStepTwoPage:
    step_one = _go_to_checkout_step_one(page)
    step_one.fill_customer_info(**CUSTOMER)
    step_one.continue_to_overview()
    return CheckoutStepTwoPage(page)


def _go_to_checkout_complete(page: Page) -> CheckoutCompletePage:
    step_two = _go_to_checkout_step_two(page)
    step_two.finish_order()
    return CheckoutCompletePage(page)


class TestSidebarMenu:
    def test_open_and_close_sidebar(self, logged_in_page: Page) -> None:
        products = ProductPage(logged_in_page)

        products.sidebar.open()
        products.sidebar.assert_menu_visible()
        products.sidebar.close()
        products.sidebar.assert_menu_hidden()

    def test_all_items_navigation_returns_to_products(self, logged_in_page: Page) -> None:
        cart = _go_to_cart(logged_in_page)

        cart.sidebar.go_to_all_items()

        ProductPage(logged_in_page).assert_on_products_page()

    def test_products_navigation_returns_to_products(self, logged_in_page: Page) -> None:
        cart = _go_to_cart(logged_in_page)

        cart.sidebar.go_to_products()

        ProductPage(logged_in_page).assert_on_products_page()

    def test_logout_returns_to_login_page(self, logged_in_page: Page) -> None:
        products = ProductPage(logged_in_page)

        products.sidebar.logout()

        LoginPage(logged_in_page).assert_on_login_page()

    def test_reset_app_state_clears_cart_badge(self, logged_in_page: Page) -> None:
        products = ProductPage(logged_in_page)

        products.add_item_to_cart(SAUCE_LABS_BACKPACK)
        products.assert_cart_badge_count(1)

        products.sidebar.reset_app_state()

        products.assert_cart_badge_not_visible()

    @pytest.mark.xfail(
        reason="standard_user: Reset App State clears cart state but leaves the current item button as Remove until reload"
    )
    def test_reset_app_state_restores_add_to_cart_button(self, logged_in_page: Page) -> None:
        products = ProductPage(logged_in_page)

        products.add_item_to_cart(SAUCE_LABS_BACKPACK)
        products.assert_item_marked_in_cart(SAUCE_LABS_BACKPACK)

        products.sidebar.reset_app_state()

        products.assert_item_can_be_added(SAUCE_LABS_BACKPACK)

    def test_about_link_navigates_to_saucelabs(self, logged_in_page: Page) -> None:
        products = ProductPage(logged_in_page)

        products.sidebar.click_about()

        products.sidebar.assert_on_about_destination()

    def test_sidebar_is_available_on_products_page(self, logged_in_page: Page) -> None:
        ProductPage(logged_in_page).sidebar.assert_authenticated_menu_available()

    def test_sidebar_is_available_on_cart_page(self, logged_in_page: Page) -> None:
        cart = _go_to_cart(logged_in_page)

        cart.sidebar.assert_authenticated_menu_available()

    def test_sidebar_is_available_on_checkout_step_one(self, logged_in_page: Page) -> None:
        step_one = _go_to_checkout_step_one(logged_in_page)

        step_one.sidebar.assert_authenticated_menu_available()

    def test_sidebar_is_available_on_checkout_step_two(self, logged_in_page: Page) -> None:
        step_two = _go_to_checkout_step_two(logged_in_page)

        step_two.sidebar.assert_authenticated_menu_available()

    def test_sidebar_is_available_on_checkout_complete(self, logged_in_page: Page) -> None:
        complete = _go_to_checkout_complete(logged_in_page)

        complete.sidebar.assert_authenticated_menu_available()