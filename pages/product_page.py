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
    HEADER = ".header_container"
    INVENTORY_ITEM = ".inventory_item"
    INVENTORY_ITEM_DESCRIPTION = ".inventory_item_description"
    INVENTORY_ITEM_PRICE = ".inventory_item_price"
    INVENTORY_ITEM_BUTTON = ".pricebar button"

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

    def assert_catalog_prices(self, expected_prices: list[float]) -> None:
        raw = self._page.locator(self.PRODUCT_PRICES).all_text_contents()
        actual_prices = [float(price.replace("$", "")) for price in raw]
        assert actual_prices == expected_prices, (
            f"Expected catalog prices {expected_prices}, got {actual_prices}"
        )

    def assert_cart_badge_count(self, expected: int) -> None:
        expect(self._page.locator(self.CART_BADGE)).to_have_text(str(expected))

    def assert_cart_badge_not_visible(self) -> None:
        expect(self._page.locator(self.CART_BADGE)).not_to_be_visible()

    def assert_item_can_be_added(self, item_name: str) -> None:
        data_test = f"add-to-cart-{item_name.lower().replace(' ', '-')}"
        expect(self._page.locator(f"[data-test='{data_test}']")).to_be_visible()

    def assert_item_marked_in_cart(self, item_name: str) -> None:
        data_test = f"remove-{item_name.lower().replace(' ', '-')}"
        expect(self._page.locator(f"[data-test='{data_test}']")).to_be_visible()

    def assert_cart_icon_is_positioned_top_right(self) -> None:
        header = self._page.locator(self.HEADER)
        cart = self._page.locator(self.CART_LINK)

        expect(header).to_be_visible()
        expect(cart).to_be_visible()

        header_box = header.bounding_box()
        cart_box = cart.bounding_box()

        assert header_box is not None, "Header bounding box could not be determined"
        assert cart_box is not None, "Cart icon bounding box could not be determined"

        cart_center_x = cart_box["x"] + cart_box["width"] / 2
        cart_center_y = cart_box["y"] + cart_box["height"] / 2
        header_right_threshold = header_box["x"] + header_box["width"] * 0.85

        assert header_box["y"] <= cart_center_y <= header_box["y"] + header_box["height"], (
            f"Expected cart icon to stay within header vertically, got y={cart_center_y}"
        )
        assert cart_center_x >= header_right_threshold, (
            f"Expected cart icon near the right side of the header, got center x={cart_center_x}"
        )

    def assert_first_product_pricebar_has_compact_spacing(
        self,
        max_gap_px: float = 90.0,
    ) -> None:
        items = self._page.locator(self.INVENTORY_ITEM)
        item_count = items.count()
        indices_to_check = sorted({0, item_count // 2, item_count - 1})

        for index in indices_to_check:
            item = items.nth(index)
            price = item.locator(self.INVENTORY_ITEM_PRICE)
            button = item.locator(self.INVENTORY_ITEM_BUTTON)

            expect(item).to_be_visible()
            expect(price).to_be_visible()
            expect(button).to_be_visible()

            price_box = price.bounding_box()
            button_box = button.bounding_box()

            assert price_box is not None, f"Price bounding box could not be determined for item {index}"
            assert button_box is not None, f"Add to cart button bounding box could not be determined for item {index}"

            horizontal_gap = button_box["x"] - (price_box["x"] + price_box["width"])
            vertical_center_delta = abs(
                (button_box["y"] + button_box["height"] / 2)
                - (price_box["y"] + price_box["height"] / 2)
            )

            assert vertical_center_delta <= 12, (
                f"Expected price and button to stay on the same row for item {index}, got center delta {vertical_center_delta}px"
            )
            assert horizontal_gap >= -2, (
                f"Expected button not to overlap the price for item {index}, got gap {horizontal_gap}px"
            )
            assert horizontal_gap <= max_gap_px, (
                f"Expected compact spacing between price and button for item {index}, got gap {horizontal_gap}px"
            )