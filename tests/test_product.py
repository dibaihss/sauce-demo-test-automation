"""
Tests for the SauceDemo Products page.

Covers:
- Product sorting (A→Z, Z→A, price low→high, price high→low)
- Adding a single item to the cart
- Adding multiple items to the cart
- Removing an item from the products page
- Cross-user checks: same behaviors tested with all user accounts
"""
import pytest
from playwright.sync_api import Page

from pages.product_page import ProductPage


SAUCE_LABS_BACKPACK = "Sauce Labs Backpack"
SAUCE_LABS_BIKE_LIGHT = "Sauce Labs Bike Light"


class TestProductSorting:
    def test_sort_a_to_z(self, logged_in_page: Page) -> None:
        products = ProductPage(logged_in_page)
        products.sort_by("az")
        products.assert_product_names_sorted_ascending()

    def test_sort_z_to_a(self, logged_in_page: Page) -> None:
        products = ProductPage(logged_in_page)
        products.sort_by("za")
        products.assert_product_names_sorted_descending()

    def test_sort_price_low_to_high(self, logged_in_page: Page) -> None:
        products = ProductPage(logged_in_page)
        products.sort_by("lohi")
        products.assert_prices_sorted_low_to_high()

    def test_sort_price_high_to_low(self, logged_in_page: Page) -> None:
        products = ProductPage(logged_in_page)
        products.sort_by("hilo")
        products.assert_prices_sorted_high_to_low()


class TestCartManagement:
    def test_add_single_item_updates_badge(self, logged_in_page: Page) -> None:
        products = ProductPage(logged_in_page)
        products.add_item_to_cart(SAUCE_LABS_BACKPACK)
        products.assert_cart_badge_count(1)

    def test_add_multiple_items_updates_badge(self, logged_in_page: Page) -> None:
        products = ProductPage(logged_in_page)
        products.add_item_to_cart(SAUCE_LABS_BACKPACK)
        products.add_item_to_cart(SAUCE_LABS_BIKE_LIGHT)
        products.assert_cart_badge_count(2)

    def test_remove_item_from_products_page(self, logged_in_page: Page) -> None:
        products = ProductPage(logged_in_page)
        products.add_item_to_cart(SAUCE_LABS_BACKPACK)
        products.assert_cart_badge_count(1)
        products.remove_item_from_cart(SAUCE_LABS_BACKPACK)
        products.assert_cart_badge_not_visible()

    def test_add_all_items_to_cart(self, logged_in_page: Page) -> None:
        """All 6 products items can be added — badge should show 6."""
        products = ProductPage(logged_in_page)
        add_buttons = logged_in_page.locator("[data-test^='add-to-cart']")
        # Count before clicking — buttons disappear as we click them
        count = add_buttons.count()
        while add_buttons.count() > 0:
            add_buttons.first.click()
        products.assert_cart_badge_count(count)


# ---------------------------------------------------------------------------
# Cross-user tests — same behavior expected for every user account
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("username", [
    "standard_user",
    pytest.param("problem_user", marks=pytest.mark.xfail(
        reason="problem_user: alle Produktbilder haben dieselbe src"
    )),
    "performance_glitch_user",
    "error_user",
    "visual_user",
])
def test_each_product_has_unique_image(logged_in_page_as, username: str) -> None:
    """Every product must display its own unique image."""
    page = logged_in_page_as(username)
    images = page.locator(".inventory_item img").all()
    srcs = [img.get_attribute("src") for img in images]
    assert len(set(srcs)) == len(srcs), (
        f"Duplicate product images found for {username}: {set(srcs)}"
    )


@pytest.mark.parametrize("username", [
    "standard_user",
    pytest.param("problem_user", marks=pytest.mark.xfail(
        reason="problem_user: Z→A Sortierung hat keinen Effekt"
    )),
    "performance_glitch_user",
    pytest.param("error_user", marks=pytest.mark.xfail(
        reason="error_user: Z→A Sortierung hat keinen Effekt"
    )),
    "visual_user",
])
def test_sort_za_orders_products_correctly(logged_in_page_as, username: str) -> None:
    """Selecting Z→A must reorder the product list in descending order."""
    page = logged_in_page_as(username)
    products = ProductPage(page)
    products.sort_by("za")
    products.assert_product_names_sorted_descending()


@pytest.mark.parametrize("username", [
    "standard_user",
    "problem_user",
    "performance_glitch_user",
    "error_user",
    "visual_user",
])
def test_add_to_cart_updates_badge(logged_in_page_as, username: str) -> None:
    """Adding an item must increment the cart badge to 1."""
    page = logged_in_page_as(username)
    products = ProductPage(page)
    products.add_item_to_cart(SAUCE_LABS_BACKPACK)
    products.assert_cart_badge_count(1)