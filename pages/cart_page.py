"""Page Object for the SauceDemo Cart page."""
from playwright.sync_api import Page, expect

from pages.sidebar_menu import SidebarMenu


class CartPage:
    CART_ITEMS = ".cart_item"
    ITEM_NAMES = ".inventory_item_name"
    CHECKOUT_BUTTON = "[data-test='checkout']"
    CONTINUE_SHOPPING_BUTTON = "[data-test='continue-shopping']"
    REMOVE_BUTTON_TPL = "[data-test='remove-{slug}']"
    CART_CONTENTS = "#cart_contents_container"

    def __init__(self, page: Page) -> None:
        self._page = page
        self.sidebar = SidebarMenu(page)

    # --- Actions ---
    def proceed_to_checkout(self) -> None:
        self._page.click(self.CHECKOUT_BUTTON)
        self._page.wait_for_url("**/checkout-step-one.html")

    def continue_shopping(self) -> None:
        self._page.click(self.CONTINUE_SHOPPING_BUTTON)
        self._page.wait_for_url("**/inventory.html")

    def remove_item(self, item_name: str) -> None:
        slug = item_name.lower().replace(" ", "-")
        self._page.click(self.REMOVE_BUTTON_TPL.format(slug=slug))

    # --- Assertions ---
    def assert_item_in_cart(self, item_name: str) -> None:
        expect(self._page.locator(self.ITEM_NAMES).filter(has_text=item_name)).to_be_visible()

    def assert_item_not_in_cart(self, item_name: str) -> None:
        expect(self._page.locator(self.ITEM_NAMES).filter(has_text=item_name)).not_to_be_visible()

    def assert_cart_is_empty(self) -> None:
        expect(self._page.locator(self.CART_ITEMS)).to_have_count(0)

    def assert_checkout_button_stays_in_cart_footer(self) -> None:
        cart_contents = self._page.locator(self.CART_CONTENTS)
        first_item = self._page.locator(self.CART_ITEMS).first
        checkout_button = self._page.locator(self.CHECKOUT_BUTTON)

        expect(cart_contents).to_be_visible()
        expect(first_item).to_be_visible()
        expect(checkout_button).to_be_visible()

        contents_box = cart_contents.bounding_box()
        item_box = first_item.bounding_box()
        checkout_box = checkout_button.bounding_box()

        assert contents_box is not None, "Cart contents bounding box could not be determined"
        assert item_box is not None, "Cart item bounding box could not be determined"
        assert checkout_box is not None, "Checkout button bounding box could not be determined"

        checkout_center_y = checkout_box["y"] + checkout_box["height"] / 2

        assert contents_box["y"] <= checkout_center_y <= contents_box["y"] + contents_box["height"], (
            f"Expected checkout button inside the cart contents area, got y={checkout_center_y}"
        )
        assert checkout_box["y"] > item_box["y"] + item_box["height"], (
            f"Expected checkout button below the cart items, got y={checkout_box['y']}"
        )
