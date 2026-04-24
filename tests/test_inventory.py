"""
Tests for the SauceDemo Inventory page.

Covers:
- Product sorting (A→Z, Z→A, price low→high, price high→low)
- Adding a single item to the cart
- Adding multiple items to the cart
- Removing an item from the inventory page
"""
import pytest
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage


SAUCE_LABS_BACKPACK = "Sauce Labs Backpack"
SAUCE_LABS_BIKE_LIGHT = "Sauce Labs Bike Light"


class TestProductSorting:
    def test_sort_a_to_z(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.sort_by("az")
        inventory.assert_product_names_sorted_ascending()

    def test_sort_z_to_a(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.sort_by("za")
        inventory.assert_product_names_sorted_descending()

    def test_sort_price_low_to_high(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.sort_by("lohi")
        inventory.assert_prices_sorted_low_to_high()

    def test_sort_price_high_to_low(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.sort_by("hilo")
        inventory.assert_prices_sorted_high_to_low()


class TestCartManagement:
    def test_add_single_item_updates_badge(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart(SAUCE_LABS_BACKPACK)
        inventory.assert_cart_badge_count(1)

    def test_add_multiple_items_updates_badge(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart(SAUCE_LABS_BACKPACK)
        inventory.add_item_to_cart(SAUCE_LABS_BIKE_LIGHT)
        inventory.assert_cart_badge_count(2)

    def test_remove_item_from_inventory_page(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart(SAUCE_LABS_BACKPACK)
        inventory.assert_cart_badge_count(1)
        inventory.remove_item_from_cart(SAUCE_LABS_BACKPACK)
        inventory.assert_cart_badge_not_visible()

    def test_add_all_items_to_cart(self, logged_in_page: Page) -> None:
        """All 6 inventory items can be added — badge should show 6."""
        inventory = InventoryPage(logged_in_page)
        add_buttons = logged_in_page.locator("[data-test^='add-to-cart']")
        # Count before clicking — buttons disappear as we click them
        count = add_buttons.count()
        while add_buttons.count() > 0:
            add_buttons.first.click()
        inventory.assert_cart_badge_count(count)
