"""Page Object for the SauceDemo Cart page."""
from playwright.sync_api import Page, expect


class CartPage:
    CART_ITEMS = ".cart_item"
    ITEM_NAMES = ".inventory_item_name"
    CHECKOUT_BUTTON = "[data-test='checkout']"
    CONTINUE_SHOPPING_BUTTON = "[data-test='continue-shopping']"
    REMOVE_BUTTON_TPL = "[data-test='remove-{slug}']"

    def __init__(self, page: Page) -> None:
        self._page = page

    # --- Actions ---
    def proceed_to_checkout(self) -> None:
        self._page.click(self.CHECKOUT_BUTTON)
        self._page.wait_for_url("**/checkout-step-one.html")

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
