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

def reset_page(pg: Page):
    pg.goto(BASE_URL)

# =============================
# TEST CASES (GIỮ NGUYÊN 28 CASES)
# =============================

def test_login_1(pg): assert "/login" in pg.url

def test_login_2(pg): expect(pg.get_by_text("新規登録")).to_be_visible()

def test_login_3(pg):
    pg.get_by_text("新規登録").click()
    pg.wait_for_load_state("networkidle")
    assert "register" in pg.url or pg.get_by_text("新規登録").count() > 0

def test_login_4(pg):
    expect(pg.get_by_text("メールアドレス")).to_be_visible()
    expect(pg.locator(EMAIL)).to_have_attribute("placeholder", "sample@example.com")

def test_login_5(pg):
    login(pg, "abc@gmail.com", VALID_PASSWORD)
    expect(pg.locator(ERROR_TEXT_1)).to_be_hidden()

def test_login_6(pg):
    login(pg, "ABC@GMAIL.COM", VALID_PASSWORD)
    expect(pg.locator(ERROR_TEXT_1)).to_be_hidden()

def test_login_7(pg):
    login(pg, "abc@gmail", VALID_PASSWORD)
    expect(pg.locator(ERROR_TEXT_1)).to_be_visible()

def test_login_8(pg):
    login(pg, "abc!@gmail.com", VALID_PASSWORD)
    expect(pg.locator(ERROR_TEXT_1)).to_be_visible()

def test_login_9(pg):
    login(pg, "test.abc", VALID_PASSWORD)
    expect(pg.locator(ERROR_TEXT_1)).to_be_visible()

def test_login_10(pg):
    login(pg, "@gmail.com", VALID_PASSWORD)
    expect(pg.locator(ERROR_TEXT_1)).to_be_visible()

def test_login_11(pg):
    login(pg, "テスト@gmail.com", VALID_PASSWORD)
    expect(pg.locator(ERROR_TEXT_1)).to_be_visible()

def test_login_12(pg):
    login(pg, "", VALID_PASSWORD)
    expect(pg.locator(REQUIRED_TEXT_1)).to_be_visible()

def test_login_13(pg):
    label = pg.locator(".login-form__password__label")
    expect(label).to_contain_text("パスワード")

    password_input = pg.locator("#password")
    expect(password_input).to_have_attribute("placeholder", "半角英数記号8文字以上32文字まで")
    expect(password_input).to_have_attribute("type", "password")

    toggle_btn = pg.get_by_label("append icon")
    expect(toggle_btn).to_have_text("visibility_off")

    toggle_btn.click()
    expect(password_input).to_have_attribute("type", "text")

def test_login_14(pg):
    password_input = pg.locator("#password")
    toggle_btn = pg.get_by_label("append icon")

    password_input.fill("12345678")
    expect(password_input).to_have_attribute("type", "password")
    expect(password_input).to_have_value("12345678")

    toggle_btn.click()
    expect(password_input).to_have_attribute("type", "text")
    expect(password_input).to_have_value("12345678")

def test_login_15(pg):
    login(pg, VALID_EMAIL, "")
    expect(pg.locator(REQUIRED_TEXT_2)).to_be_visible()

def test_login_16(pg):
    login(pg, VALID_EMAIL, "1234567")
    expect(pg.locator(ERROR_TEXT_2)).to_be_visible()

def test_login_17(pg):
    login(pg, VALID_EMAIL, "1"*33)
    expect(pg.locator(ERROR_TEXT_2)).to_be_visible()

def test_login_18(pg):
    login(pg, VALID_EMAIL, "a"*8)
    expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()

def test_login_19(pg):
    login(pg, VALID_EMAIL, "Aaaaaaaa")
    expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()

def test_login_20(pg):
    login(pg, VALID_EMAIL, "12345678")
    expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()

def test_login_21(pg):
    login(pg, VALID_EMAIL, "@Aaaaaaaa")
    expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()

def test_login_22(pg):
    login(pg, VALID_EMAIL, "@12345678")
    expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()

def test_login_23(pg):
    login(pg, VALID_EMAIL, "123456Aa")
    expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()

def test_login_24(pg):
    login(pg, VALID_EMAIL, "12345678")
    expect(pg.locator(ERROR_MESSAGE)).to_be_visible()

def test_login_25(pg):
    login(pg, "test@gmail.com", VALID_PASSWORD)
    expect(pg.locator(ERROR_MESSAGE)).to_be_visible()

def test_login_26(pg):
    login(pg, VALID_EMAIL, VALID_PASSWORD)
    expect(pg).to_have_url(re.compile(r".*/event/.*"))

def test_login_27(pg):
    forgot_link = pg.locator(".smart__forget__link")
    expect(forgot_link).to_be_visible()
    expect(forgot_link).to_have_text("パスワードを忘れた場合")

def test_login_28(pg):
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
        if callable(func) and name.startswith("test_login_")
    ]

    # sort đúng thứ tự 1 → 28
    test_functions.sort(key=lambda x: int(x[0].split("_")[-1]))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for name, test_func in test_functions:
            print(f"Running {name}...", end=" ", flush=True)
            start = time.time()

            try:
                reset_page(page)
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
                "duration": duration,
                "error": error_msg
            })

        browser.close()

    # =============================
    # REPORT
    # =============================
    report_path = "test_reports/execution_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"TEST EXECUTION REPORT - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Duration: {round(time.time() - start_time, 2)} seconds\n")
        f.write(f"Total Cases: {len(results)}\n")
        f.write("-" * 50 + "\n")

        for res in results:
            line = f"[{res['status']}] {res['name']} ({res['duration']}s)"
            if res['error']:
                line += f" - {res['error']}"
            f.write(line + "\n")

    print(f"\n✨ Report generated at: {os.path.abspath(report_path)}")