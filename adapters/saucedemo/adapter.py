from __future__ import annotations
from typing import Any, Dict
from adapters.base import SUTAdapter, TestResult
from adapters.registry import register

from playwright.sync_api import sync_playwright
import time

@register("saucedemo")
class SauceDemoAdapter(SUTAdapter):
    def __init__(self, sut_config: Dict[str, Any]):
        super().__init__(sut_config)
        self._visited_pages = set()   # ✅ track what we covered

    @property
    def type_name(self) -> str:
        return "saucedemo"

    def _mark_page(self, page_name: str) -> None:
        self._visited_pages.add(page_name)

    def healthcheck(self) -> bool:
        base_url = self.sut_config["base_url"].rstrip("/")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(base_url, wait_until="domcontentloaded", timeout=15000)
                browser.close()
            return True
        except Exception:
            return False

    def execute_testcase(self, testcase: Dict[str, Any]) -> TestResult:
        return TestResult(
            testcase_id=testcase.get("id", "UNKNOWN"),
            status="skipped",
            details="SauceDemoAdapter currently runs in suite mode."
        )

    # ✅ This is your SauceDemo 'coverage'
    def collect_coverage(self) -> dict:
        modeled_pages = ["login", "inventory", "cart", "checkout"]
        visited = self._visited_pages

        return {
            "available": True,
            "type": "ui_page_coverage",
            "modeled_pages": modeled_pages,
            "visited_pages": sorted(list(visited)),
            "page_coverage_percent": round(100 * len(visited) / len(modeled_pages), 2),
        }

    def run_suite(self) -> dict:
        start = time.time()
        base_url = self.sut_config["base_url"].rstrip("/")
        username = self.sut_config["auth"]["user"]["username"]
        password = self.sut_config["auth"]["user"]["password"]

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # ---- login page
                page.goto(base_url, wait_until="domcontentloaded", timeout=15000)
                self._mark_page("login")

                # valid login -> inventory
                page.locator("#user-name").fill(username)
                page.locator("#password").fill(password)
                page.locator("#login-button").click()
                page.wait_for_url("**/inventory.html", timeout=15000)
                self._mark_page("inventory")

                # OPTIONAL: visit cart (adds "cart" coverage)
                page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
                page.locator(".shopping_cart_link").click()
                page.wait_for_url("**/cart.html", timeout=15000)
                self._mark_page("cart")

                # OPTIONAL: start checkout (adds "checkout" coverage)
                page.locator('[data-test="checkout"]').click()
                page.wait_for_url("**/checkout-step-one.html", timeout=15000)
                self._mark_page("checkout")

                # invalid login test (back to login)
                page.goto(base_url, wait_until="domcontentloaded", timeout=15000)
                self._mark_page("login")

                page.locator("#user-name").fill("invalid_user")
                page.locator("#password").fill("wrong_password")
                page.locator("#login-button").click()

                browser.close()

            return {"status": "passed", "details": "Suite passed.", "duration_s": round(time.time()-start, 3)}
        except Exception as e:
            return {"status": "error", "details": str(e)}
