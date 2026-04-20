import os
import re
import time
import traceback
from playwright.sync_api import sync_playwright, expect, Page

# =============================
# CONFIG
# =============================
BASE_URL = "https://playwright-demo.eventos.work/web/portal/529/event/3988/users/login"

VALID_EMAIL = "phuongtest111@gmail.com"
VALID_PASSWORD = "Aa123456"

EMAIL = "input[type='email']"
PASSWORD = "input[type='password']"
LOGIN_BTN = "button:has-text('ログイン')"

ERROR_TEXT_1 = "text=メールアドレスが正しくありません"
ERROR_TEXT_2 = "text=パスワードは8文字以上32文字以下で指定してください"

REQUIRED_TEXT_1 = "text=メールアドレスを入力してください"
REQUIRED_TEXT_2 = "text=パスワードを入力してください"

ERROR_MESSAGE = "text=ログインできませんでした。入力内容をご確認の上、もう一度お試しください"

# =============================
# HELPERS
# =============================
def login(pg: Page, email: str, password: str):
    pg.fill(EMAIL, email)
    pg.fill(PASSWORD, password)
    pg.click(LOGIN_BTN)


# =============================
# TEST CASES
# =============================

def test_login_1(pg):
    assert "/login" in pg.url


def test_login_2(pg):
    expect(pg.get_by_text("新規登録")).to_be_visible()


def test_login_3(pg):
    pg.get_by_text("新規登録").click()
    pg.wait_for_load_state("networkidle")
    assert "register" in pg.url or pg.get_by_text("新規登録").count() > 0


def test_login_4(pg):
    expect(pg.get_by_text("メールアドレス")).to_be_visible()
    expect(pg.locator(EMAIL)).to_have_attribute("placeholder", "sample@example.com")


# =============================
# EMAIL VALIDATION (DATA DRIVEN)
# =============================
INVALID_EMAILS = [
    "abc@gmail",
    "abc!@gmail.com",
    "test.abc",
    "@gmail.com",
    "テスト@gmail.com"
]

def test_invalid_emails(pg):
    for email in INVALID_EMAILS:
        login(pg, email, VALID_PASSWORD)
        expect(pg.locator(ERROR_TEXT_1)).to_be_visible()
        pg.reload()


def test_valid_email_lower(pg):
    login(pg, "abc@gmail.com", VALID_PASSWORD)
    expect(pg.locator(ERROR_TEXT_1)).to_be_hidden()


def test_valid_email_upper(pg):
    login(pg, "ABC@GMAIL.COM", VALID_PASSWORD)
    expect(pg.locator(ERROR_TEXT_1)).to_be_hidden()


def test_empty_email(pg):
    login(pg, "", VALID_PASSWORD)
    expect(pg.locator(REQUIRED_TEXT_1)).to_be_visible()


# =============================
# PASSWORD UI
# =============================

def test_password_ui(pg):
    label = pg.locator(".login-form__password__label")
    expect(label).to_contain_text("パスワード")

    password_input = pg.locator("#password")
    expect(password_input).to_have_attribute("placeholder", "半角英数記号8文字以上32文字まで")
    expect(password_input).to_have_attribute("type", "password")

    toggle_btn = pg.get_by_label("append icon")
    expect(toggle_btn).to_have_text("visibility_off")

    toggle_btn.click()
    expect(password_input).to_have_attribute("type", "text")


def test_password_toggle(pg):
    password_input = pg.locator("#password")
    toggle_btn = pg.get_by_label("append icon")

    password_input.fill("12345678")

    expect(password_input).to_have_attribute("type", "password")
    expect(password_input).to_have_value("12345678")

    toggle_btn.click()

    expect(password_input).to_have_attribute("type", "text")
    expect(password_input).to_have_value("12345678")


# =============================
# PASSWORD VALIDATION
# =============================

def test_empty_password(pg):
    login(pg, VALID_EMAIL, "")
    expect(pg.locator(REQUIRED_TEXT_2)).to_be_visible()


def test_short_password(pg):
    login(pg, VALID_EMAIL, "1234567")
    expect(pg.locator(ERROR_TEXT_2)).to_be_visible()


def test_long_password(pg):
    login(pg, VALID_EMAIL, "1" * 33)
    expect(pg.locator(ERROR_TEXT_2)).to_be_visible()


VALID_PASSWORD_CASES = [
    "a"*8,
    "Aaaaaaaa",
    "12345678",
    "@Aaaaaaaa",
    "@12345678",
    "123456Aa"
]

def test_valid_passwords(pg):
    for pwd in VALID_PASSWORD_CASES:
        login(pg, VALID_EMAIL, pwd)
        expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()
        pg.reload()


# =============================
# LOGIN FLOW
# =============================

def test_wrong_credentials(pg):
    login(pg, VALID_EMAIL, "12345678")
    expect(pg.locator(ERROR_MESSAGE)).to_be_visible()


def test_wrong_email(pg):
    login(pg, "test@gmail.com", VALID_PASSWORD)
    expect(pg.locator(ERROR_MESSAGE)).to_be_visible()


def test_success_login(pg):
    login(pg, VALID_EMAIL, VALID_PASSWORD)
    expect(pg).to_have_url(re.compile(r".*/event/.*"))


# =============================
# FORGOT PASSWORD
# =============================

def test_forgot_password_ui(pg):
    forgot_link = pg.locator(".smart__forget__link")
    expect(forgot_link).to_be_visible()
    expect(forgot_link).to_have_text("パスワードを忘れた場合")


def test_forgot_password_navigation(pg):
    forgot_link = pg.locator(".smart__forget__link")
    forgot_link.click()
    pg.wait_for_load_state("networkidle")
    expect(pg).to_have_url(re.compile(r".*/reset.*"))


# =============================
# RUNNER
# =============================
if __name__ == "__main__":
    start_time = time.time()
    results = []

    os.makedirs("test_reports/screenshots", exist_ok=True)

    test_functions = [
        (name, func) for name, func in globals().items()
        if callable(func) and name.startswith("test_")
    ]
    test_functions.sort(key=lambda x: x[0])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for name, test_func in test_functions:
            print(f"Running {name}...", end=" ", flush=True)
            start = time.time()

            try:
                page.goto(BASE_URL)
                test_func(page)
                status = "PASSED"
                error_msg = ""
                print("✅ PASSED")

            except Exception as e:
                status = "FAILED"
                error_msg = str(e)
                print("❌ FAILED")

                page.screenshot(path=f"test_reports/screenshots/{name}.png")
                with open(f"test_reports/screenshots/{name}_error.txt", "w", encoding="utf-8") as f:
                    f.write(traceback.format_exc())

            duration = round(time.time() - start, 2)

            results.append({
                "name": name,
                "status": status,
                "error": error_msg,
                "duration": duration
            })

        browser.close()

    # =============================
    # REPORT
    # =============================
    report_path = "test_reports/execution_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"TEST EXECUTION REPORT - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Duration: {round(time.time() - start_time, 2)} seconds\n")
        f.write("-" * 50 + "\n")

        for res in results:
            line = f"[{res['status']}] {res['name']} ({res['duration']}s)"
            if res['error']:
                line += f" - Error: {res['error']}"
            f.write(line + "\n")

    print(f"\n✨ Report generated at: {os.path.abspath(report_path)}")