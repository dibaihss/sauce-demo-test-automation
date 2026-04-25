"""Page Object for the SauceDemo Products page."""
from playwright.sync_api import Page, expect

from pages.sidebar_menu import SidebarMenu


class ProductPage:
    SORT_DROPDOWN = "[data-test='product-sort-container']"
    PRODUCT_NAMES = ".inventory_item_name"
    PRODUCT_PRICES = ".inventory_item_price"
    ADD_TO_CART_BUTTONS = "[data-test^='add-to-cart']"
    REMOVE_BUTTONS = "[data-test^='remove']"
    CART_BADGE = ".shopping_cart_badge"
    CART_LINK = ".shopping_cart_link"

    def __init__(self, page: Page) -> None:
        self._page = page
        self.sidebar = SidebarMenu(page)

    # --- Actions ---
    def sort_by(self, option_value: str) -> None:
        """Sort products. option_value: 'az', 'za', 'lohi', 'hilo'."""
        self._page.select_option(self.SORT_DROPDOWN, option_value)

    def add_item_to_cart(self, item_name: str) -> None:
        data_test = f"add-to-cart-{item_name.lower().replace(' ', '-')}"
        self._page.click(f"[data-test='{data_test}']")

    def remove_item_from_cart(self, item_name: str) -> None:
        data_test = f"remove-{item_name.lower().replace(' ', '-')}"
        self._page.click(f"[data-test='{data_test}']")

    def go_to_cart(self) -> None:
        self._page.click(self.CART_LINK)
        self._page.wait_for_url("**/cart.html")

    def assert_on_products_page(self) -> None:
        self._page.wait_for_url("**/inventory.html")
        expect(self._page.locator(".title")).to_have_text("Products")

    # --- Assertions ---
    def assert_product_names_sorted_ascending(self) -> None:
        names = self._page.locator(self.PRODUCT_NAMES).all_text_contents()
        assert names == sorted(names), f"Expected A→Z, got: {names}"

    def assert_product_names_sorted_descending(self) -> None:
        names = self._page.locator(self.PRODUCT_NAMES).all_text_contents()
        assert names == sorted(names, reverse=True), f"Expected Z→A, got: {names}"

    def assert_prices_sorted_low_to_high(self) -> None:
        raw = self._page.locator(self.PRODUCT_PRICES).all_text_contents()
        prices = [float(p.replace("$", "")) for p in raw]
        assert prices == sorted(prices), f"Expected low→high, got: {prices}"

    def assert_prices_sorted_high_to_low(self) -> None:
        raw = self._page.locator(self.PRODUCT_PRICES).all_text_contents()
        prices = [float(p.replace("$", "")) for p in raw]
        assert prices == sorted(prices, reverse=True), f"Expected high→low, got: {prices}"

    def assert_cart_badge_count(self, expected: int) -> None:
        expect(self._page.locator(self.CART_BADGE)).to_have_text(str(expected))

    def assert_cart_badge_not_visible(self) -> None:
        expect(self._page.locator(self.CART_BADGE)).not_to_be_visible()