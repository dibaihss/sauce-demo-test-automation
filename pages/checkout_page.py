"""Page Objects for the SauceDemo Checkout flow (Step 1, Step 2, Confirmation)."""
from playwright.sync_api import Page, expect


class CheckoutStepOnePage:
    FIRST_NAME = "[data-test='firstName']"
    LAST_NAME = "[data-test='lastName']"
    POSTAL_CODE = "[data-test='postalCode']"
    CONTINUE_BUTTON = "[data-test='continue']"
    ERROR_MESSAGE = "[data-test='error']"

    def __init__(self, page: Page) -> None:
        self._page = page

    def fill_customer_info(self, first: str, last: str, postal: str) -> None:
        self._page.fill(self.FIRST_NAME, first)
        self._page.fill(self.LAST_NAME, last)
        self._page.fill(self.POSTAL_CODE, postal)

    def continue_to_overview(self) -> None:
        self._page.click(self.CONTINUE_BUTTON)
        self._page.wait_for_url("**/checkout-step-two.html")

    def assert_error_message(self, expected_text: str) -> None:
        expect(self._page.locator(self.ERROR_MESSAGE)).to_have_text(expected_text)


class CheckoutStepTwoPage:
    ITEM_NAMES = ".inventory_item_name"
    ITEM_TOTAL = ".summary_subtotal_label"
    FINISH_BUTTON = "[data-test='finish']"

    def __init__(self, page: Page) -> None:
        self._page = page

    def finish_order(self) -> None:
        self._page.click(self.FINISH_BUTTON)
        self._page.wait_for_url("**/checkout-complete.html")

    def assert_item_listed(self, item_name: str) -> None:
        expect(self._page.locator(self.ITEM_NAMES).filter(has_text=item_name)).to_be_visible()

    def get_item_total(self) -> float:
        raw = self._page.locator(self.ITEM_TOTAL).text_content()
        # "Item total: $29.99" → 29.99
        return float(raw.split("$")[1])


class CheckoutCompletePage:
    CONFIRMATION_HEADER = ".complete-header"
    BACK_HOME_BUTTON = "[data-test='back-to-products']"
    EXPECTED_HEADER = "Thank you for your order!"

    def __init__(self, page: Page) -> None:
        self._page = page

    def assert_order_confirmed(self) -> None:
        expect(self._page.locator(self.CONFIRMATION_HEADER)).to_have_text(
            self.EXPECTED_HEADER
        )

    def go_back_home(self) -> None:
        self._page.click(self.BACK_HOME_BUTTON)
        self._page.wait_for_url("**/inventory.html")
