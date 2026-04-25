"""Reusable sidebar menu component for authenticated SauceDemo pages."""
from playwright.sync_api import Page, expect


class SidebarMenu:
    MENU_BUTTON = "#react-burger-menu-btn"
    CLOSE_BUTTON = "#react-burger-cross-btn"
    ALL_ITEMS_LINK = "#inventory_sidebar_link"
    ABOUT_LINK = "#about_sidebar_link"
    LOGOUT_LINK = "#logout_sidebar_link"
    RESET_APP_STATE_LINK = "#reset_sidebar_link"

    def __init__(self, page: Page) -> None:
        self._page = page

    def open(self) -> None:
        self._page.click(self.MENU_BUTTON)
        self.assert_menu_visible()

    def close(self) -> None:
        self._page.click(self.CLOSE_BUTTON)
        self.assert_menu_hidden()

    def go_to_all_items(self) -> None:
        self.open()
        self._page.click(self.ALL_ITEMS_LINK)
        self._page.wait_for_url("**/inventory.html")

    def go_to_products(self) -> None:
        self.go_to_all_items()

    def click_about(self) -> None:
        self.open()
        self._page.click(self.ABOUT_LINK)
        self._page.wait_for_url("**saucelabs.com/**")

    def logout(self) -> None:
        self.open()
        self._page.click(self.LOGOUT_LINK)
        self._page.wait_for_url("**/")

    def reset_app_state(self) -> None:
        self.open()
        self._page.click(self.RESET_APP_STATE_LINK)
        self.close()

    def assert_on_about_destination(self) -> None:
        assert self._page.url.startswith("https://saucelabs.com"), (
            f"Expected Sauce Labs destination, got {self._page.url}"
        )

    def assert_menu_visible(self) -> None:
        expect(self._page.locator(self.CLOSE_BUTTON)).to_be_visible()
        expect(self._page.locator(self.ALL_ITEMS_LINK)).to_be_visible()
        expect(self._page.locator(self.ABOUT_LINK)).to_be_visible()
        expect(self._page.locator(self.LOGOUT_LINK)).to_be_visible()
        expect(self._page.locator(self.RESET_APP_STATE_LINK)).to_be_visible()

    def assert_menu_hidden(self) -> None:
        expect(self._page.locator(self.CLOSE_BUTTON)).not_to_be_visible()
        expect(self._page.locator(self.ALL_ITEMS_LINK)).not_to_be_visible()

    def assert_authenticated_menu_available(self) -> None:
        expect(self._page.locator(self.MENU_BUTTON)).to_be_visible()