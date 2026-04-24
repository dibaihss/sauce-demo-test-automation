"""
Tests for the SauceDemo Checkout flow.

Covers:
- Complete happy-path checkout (add item → cart → checkout → confirm)
- Validation error on missing first name
- Removing an item inside the cart before checkout
- Back-to-products navigation after order confirmation
"""
import pytest
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutStepOnePage, CheckoutStepTwoPage, CheckoutCompletePage


SAUCE_LABS_BACKPACK = "Sauce Labs Backpack"
SAUCE_LABS_BIKE_LIGHT = "Sauce Labs Bike Light"

CUSTOMER = {"first": "Max", "last": "Mustermann", "postal": "12345"}


class TestCheckoutHappyPath:
    def test_complete_checkout_single_item(self, logged_in_page: Page) -> None:
        """Full flow: add one item → checkout → confirm order."""
        # Step 1: Add to cart
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart(SAUCE_LABS_BACKPACK)
        inventory.go_to_cart()

        # Step 2: Verify cart
        cart = CartPage(logged_in_page)
        cart.assert_item_in_cart(SAUCE_LABS_BACKPACK)
        cart.proceed_to_checkout()

        # Step 3: Fill customer info
        step_one = CheckoutStepOnePage(logged_in_page)
        step_one.fill_customer_info(**CUSTOMER)
        step_one.continue_to_overview()

        # Step 4: Verify overview & finish
        step_two = CheckoutStepTwoPage(logged_in_page)
        step_two.assert_item_listed(SAUCE_LABS_BACKPACK)
        step_two.finish_order()

        # Step 5: Confirm
        complete = CheckoutCompletePage(logged_in_page)
        complete.assert_order_confirmed()

    def test_complete_checkout_two_items(self, logged_in_page: Page) -> None:
        """Full flow with two items — both must appear in the order overview."""
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart(SAUCE_LABS_BACKPACK)
        inventory.add_item_to_cart(SAUCE_LABS_BIKE_LIGHT)
        inventory.go_to_cart()

        cart = CartPage(logged_in_page)
        cart.assert_item_in_cart(SAUCE_LABS_BACKPACK)
        cart.assert_item_in_cart(SAUCE_LABS_BIKE_LIGHT)
        cart.proceed_to_checkout()

        step_one = CheckoutStepOnePage(logged_in_page)
        step_one.fill_customer_info(**CUSTOMER)
        step_one.continue_to_overview()

        step_two = CheckoutStepTwoPage(logged_in_page)
        step_two.assert_item_listed(SAUCE_LABS_BACKPACK)
        step_two.assert_item_listed(SAUCE_LABS_BIKE_LIGHT)
        step_two.finish_order()

        CheckoutCompletePage(logged_in_page).assert_order_confirmed()

    def test_back_to_products_after_confirmation(self, logged_in_page: Page) -> None:
        """'Back Home' button navigates back to the inventory."""
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart(SAUCE_LABS_BACKPACK)
        inventory.go_to_cart()

        CartPage(logged_in_page).proceed_to_checkout()

        step_one = CheckoutStepOnePage(logged_in_page)
        step_one.fill_customer_info(**CUSTOMER)
        step_one.continue_to_overview()

        CheckoutStepTwoPage(logged_in_page).finish_order()

        complete = CheckoutCompletePage(logged_in_page)
        complete.assert_order_confirmed()
        complete.go_back_home()

        # Verify we are back on the inventory page
        from playwright.sync_api import expect
        expect(logged_in_page.locator(".title")).to_have_text("Products")


class TestCheckoutValidation:
    def test_missing_first_name_shows_error(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart(SAUCE_LABS_BACKPACK)
        inventory.go_to_cart()

        CartPage(logged_in_page).proceed_to_checkout()

        step_one = CheckoutStepOnePage(logged_in_page)
        step_one.fill_customer_info(first="", last="Mustermann", postal="12345")
        logged_in_page.click("[data-test='continue']")
        step_one.assert_error_message("Error: First Name is required")

    def test_missing_last_name_shows_error(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart(SAUCE_LABS_BACKPACK)
        inventory.go_to_cart()

        CartPage(logged_in_page).proceed_to_checkout()

        step_one = CheckoutStepOnePage(logged_in_page)
        step_one.fill_customer_info(first="Max", last="", postal="12345")
        logged_in_page.click("[data-test='continue']")
        step_one.assert_error_message("Error: Last Name is required")

    def test_missing_postal_code_shows_error(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart(SAUCE_LABS_BACKPACK)
        inventory.go_to_cart()

        CartPage(logged_in_page).proceed_to_checkout()

        step_one = CheckoutStepOnePage(logged_in_page)
        step_one.fill_customer_info(first="Max", last="Mustermann", postal="")
        logged_in_page.click("[data-test='continue']")
        step_one.assert_error_message("Error: Postal Code is required")


class TestCartPage:
    def test_remove_item_in_cart(self, logged_in_page: Page) -> None:
        """An item removed inside the cart must no longer appear there."""
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart(SAUCE_LABS_BACKPACK)
        inventory.add_item_to_cart(SAUCE_LABS_BIKE_LIGHT)
        inventory.go_to_cart()

        cart = CartPage(logged_in_page)
        cart.remove_item(SAUCE_LABS_BACKPACK)
        cart.assert_item_not_in_cart(SAUCE_LABS_BACKPACK)
        cart.assert_item_in_cart(SAUCE_LABS_BIKE_LIGHT)
