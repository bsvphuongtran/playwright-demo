import json
import re
from playwright.sync_api import sync_playwright, expect

# =============================
# CONFIG
# =============================
BASE_URL = "https://admin.odakyu.bravesoft.vn/login"
VALID_EMAIL = "kimtran@bravesoft.com.vn"
VALID_PASSWORD = "brave0404"
AUTH_FILE = "auth.json"
TOKEN_FILE = "token.json"

EMAIL = "input[name=\"email\"]"
PASSWORD = "input[type='password']"
LOGIN_BTN = "button:has-text('ログイン')"

def run_login(headless: bool = False):
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=headless)
        context = browser.new_context()
        page = context.new_page()

        page.goto(BASE_URL)
        page.fill(EMAIL, VALID_EMAIL)
        page.fill(PASSWORD, VALID_PASSWORD)
        page.locator(LOGIN_BTN).click()
        
        # QUAN TRỌNG: Phải đợi trang Quản lý tài khoản hiển thị để chắc chắn session đã được thiết lập
        expect(page.locator("div").filter(has_text=re.compile(r"^アカウント管理$"))).to_be_visible()

        print(f"✅ Đăng nhập thành công. Đang lưu trạng thái vào {AUTH_FILE}...")
        
        # Lưu lại storage_state vào file đã định nghĩa
        context.storage_state(path=AUTH_FILE)

        # Lưu token trong localStorage/sessionStorage để các file test khác có thể tái sử dụng.
        token_state = page.evaluate(
            """() => ({
                localStorage: { ...window.localStorage },
                sessionStorage: { ...window.sessionStorage }
            })"""
        )
        with open(TOKEN_FILE, "w", encoding="utf-8") as token_file:
            json.dump(token_state, token_file, ensure_ascii=False, indent=2)
        print(f"✅ Đã lưu token storage vào {TOKEN_FILE}.")
        context.close()
        browser.close()

if __name__ == "__main__":
    run_login(headless=False) # Giữ headless=False khi chạy trực tiếp Login.py để dễ debug