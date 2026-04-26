import re
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright, Browser, Page


BASE_URL = "https://www.saucedemo.com"
SCREENSHOT_DIR = Path(__file__).parent / "artifacts" / "screenshots"


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


@pytest.fixture(scope="function")
def logged_in_page_as(page: Page):
    """Factory fixture — call with any valid username to get an authenticated page."""
    def _login(username: str) -> Page:
        page.goto(BASE_URL)
        page.fill("#user-name", username)
        page.fill("#password", "secret_sauce")
        page.click("#login-button")
        page.wait_for_url("**/inventory.html")
        return page
    return _login


def _sanitize_node_id(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", nodeid).strip("_")


def _capture_screenshot(item: pytest.Item, report: pytest.TestReport, outcome: str) -> None:
    page = item.funcargs.get("page")
    if page is None or page.is_closed():
        return

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    file_name = f"{_sanitize_node_id(item.nodeid)}__{report.when}__{outcome}.png"
    screenshot_path = SCREENSHOT_DIR / file_name
    page.screenshot(path=str(screenshot_path), full_page=True)
    report.sections.append(("screenshot", f"Saved screenshot: {screenshot_path}"))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()

    if report.failed:
        _capture_screenshot(item, report, "failed")
        return

    if report.skipped and getattr(report, "wasxfail", None):
        _capture_screenshot(item, report, "xfail")
