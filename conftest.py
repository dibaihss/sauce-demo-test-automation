import pytest
from playwright.sync_api import sync_playwright, Browser, Page


BASE_URL = "https://www.saucedemo.com"


def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run tests in headless mode",
    )


@pytest.fixture(scope="session")
def browser_instance(request):
    headless = request.config.getoption("--headless")
    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch(headless=headless)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser_instance) -> Page:
    context = browser_instance.new_context(
        viewport={"width": 1280, "height": 720},
        locale="de-DE",
    )
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="function")
def logged_in_page(page: Page) -> Page:
    """Fixture that provides an already authenticated page (standard_user)."""
    page.goto(BASE_URL)
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    page.wait_for_url("**/inventory.html")
    return page
