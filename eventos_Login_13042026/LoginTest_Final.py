import os
import re
import time
import traceback
from playwright.sync_api import sync_playwright, expect

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
# TEST CASES
# =============================

def test_login_1(pg):
    assert "/login" in pg.url


def test_login_2(pg):
    expect(pg.locator("text=新規登録")).to_be_visible()


def test_login_3(pg):
    pg.click("text=新規登録")
    pg.wait_for_load_state("networkidle")
    assert "register" in pg.url or pg.locator("text=新規登録").count() > 0


def test_login_4(pg):
    expect(pg.locator("text=メールアドレス")).to_be_visible()
    expect(pg.locator("input[type='email']")).to_have_attribute("placeholder", "sample@example.com")


def test_login_5(pg):
    pg.fill(EMAIL, "abc@gmail.com")
    pg.fill(PASSWORD, VALID_PASSWORD)
    pg.click(LOGIN_BTN)
    expect(pg.locator(ERROR_TEXT_1)).to_be_hidden()


def test_login_6(pg):
    pg.fill(EMAIL, "ABC@GMAIL.COM")
    pg.fill(PASSWORD, VALID_PASSWORD)
    pg.click(LOGIN_BTN)
    expect(pg.locator(ERROR_TEXT_1)).to_be_hidden()


def test_login_7(pg):
    pg.fill(EMAIL, "abc@gmail")
    pg.fill(PASSWORD, VALID_PASSWORD)
    pg.click(LOGIN_BTN)
    expect(pg.locator(ERROR_TEXT_1)).to_be_visible()


def test_login_7(pg):
    pg.fill(EMAIL, "abc@gmail")
    pg.fill(PASSWORD, VALID_PASSWORD)
    pg.click(LOGIN_BTN)
    expect(pg.locator(ERROR_TEXT_1)).to_be_visible()


def test_login_8(pg):
    pg.fill(EMAIL, "abc!@gmail.com")
    pg.fill(PASSWORD, VALID_PASSWORD)
    pg.click(LOGIN_BTN)
    expect(pg.locator(ERROR_TEXT_1)).to_be_visible()



def test_login_9(pg):
    pg.fill(EMAIL, "test.abc")
    pg.fill(PASSWORD, VALID_PASSWORD)
    pg.click(LOGIN_BTN)
    expect(pg.locator(ERROR_TEXT_1)).to_be_visible()


def test_login_10(pg):
    pg.fill(EMAIL, "@gmail.com")
    pg.fill(PASSWORD, VALID_PASSWORD)
    pg.click(LOGIN_BTN)
    expect(pg.locator(ERROR_TEXT_1)).to_be_visible()


def test_login_11(pg):
    pg.fill(EMAIL, "テスト@gmail.com")
    pg.fill(PASSWORD, VALID_PASSWORD)
    pg.click(LOGIN_BTN)
    expect(pg.locator(ERROR_TEXT_1)).to_be_visible()
    

def test_login_12(pg):
    pg.fill(EMAIL, "")
    pg.fill(PASSWORD, VALID_PASSWORD)
    pg.click(LOGIN_BTN)
    expect(pg.locator(REQUIRED_TEXT_1)).to_be_visible()


def test_login_13(pg):
    # 1. Kiểm tra nhãn (label) sử dụng class cụ thể từ HTML snippet
    label = pg.locator(".login-form__password__label")
    expect(label).to_contain_text("パスワード")

    # 2. Kiểm tra ô input bằng ID và Placeholder chính xác
    # Sử dụng ID là cách định danh tốt nhất trong Playwright
    password_input = pg.locator("#password")
    expect(password_input).to_have_attribute("placeholder", "半角英数記号8文字以上32文字まで")
    expect(password_input).to_have_attribute("type", "password")

    # 3. Kiểm tra nút Toggle Visibility và icon (Dựa trên HTML snippet: visibility_off)
    toggle_btn = pg.get_by_label("append icon")
    expect(toggle_btn).to_have_text("visibility_off")

    # 4. Kiểm tra hành động Toggle (Chuyển đổi ẩn/hiện mật khẩu)
    toggle_btn.click()
    # Sau khi click, thuộc tính type thường chuyển sang 'text'
    expect(password_input).to_have_attribute("type", "text")


def test_login_14(pg):
    password_input = pg.locator("#password")
    toggle_btn = pg.get_by_label("append icon")

    # nhập password
    password_input.fill("12345678")

    # verify đang bị mask (type=password)
    expect(password_input).to_have_attribute("type", "password")

    # (không thể đọc "********" trực tiếp vì browser không expose giá trị mask)
    # nhưng có thể check value thật vẫn là "12345678"
    expect(password_input).to_have_value("12345678")

    # click toggle (show password)
    toggle_btn.click()

    # verify chuyển sang type=text (hiện password)
    expect(password_input).to_have_attribute("type", "text")

    # verify hiển thị đúng giá trị
    expect(password_input).to_have_value("12345678")

def test_login_15(pg):
    pg.fill(EMAIL, VALID_EMAIL)
    pg.fill(PASSWORD, "")
    pg.click(LOGIN_BTN)
    expect(pg.locator(REQUIRED_TEXT_2)).to_be_visible()

def test_login_16(pg):
    pg.fill(EMAIL, VALID_EMAIL)
    pg.fill(PASSWORD, "1234567")
    expect(pg.locator(ERROR_TEXT_2)).to_be_visible()

def test_login_17(pg):
    pg.fill(EMAIL, VALID_EMAIL)
    pg.fill(PASSWORD, "1" *33)
    expect(pg.locator(ERROR_TEXT_2)).to_be_visible()

def test_login_18(pg):
    pg.fill(EMAIL, VALID_EMAIL)
    pg.fill(PASSWORD, "a"*8)
    expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()

def test_login_19(pg):
    pg.fill(EMAIL, VALID_EMAIL)
    pg.fill(PASSWORD, "Aaaaaaaa")
    expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()

def test_login_20(pg):
    pg.fill(EMAIL, VALID_EMAIL)
    pg.fill(PASSWORD, "12345678")
    expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()

def test_login_21(pg):
    pg.fill(EMAIL, VALID_EMAIL)
    pg.fill(PASSWORD, "@Aaaaaaaa")
    expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()

def test_login_22(pg):
    pg.fill(EMAIL, VALID_EMAIL)
    pg.fill(PASSWORD, "@12345678")
    expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()

def test_login_23(pg):
    pg.fill(EMAIL, VALID_EMAIL)
    pg.fill(PASSWORD, "123456Aa")
    expect(pg.locator(ERROR_TEXT_2)).to_be_hidden()


def test_login_24(pg):
    pg.fill(EMAIL, VALID_EMAIL)
    pg.fill(PASSWORD, "12345678")
    pg.click(LOGIN_BTN)
    expect(pg.locator(ERROR_MESSAGE)).to_be_visible()

def test_login_25(pg):
    pg.fill(EMAIL, "test@gmail.com")
    pg.fill(PASSWORD, VALID_PASSWORD)
    pg.click(LOGIN_BTN)
    expect(pg.locator(ERROR_MESSAGE)).to_be_visible()

def test_login_26(pg):
    pg.fill(EMAIL, VALID_EMAIL)
    pg.fill(PASSWORD, VALID_PASSWORD)
    pg.click(LOGIN_BTN)
    #expect(pg).to_have_url("https://playwright-demo.eventos.work/web/portal/529/event/3988")
    expect(pg).to_have_url(re.compile(r".*/event/.*"))



def test_login_27(pg):
    # Sử dụng class được cung cấp để định vị liên kết quên mật khẩu một cách chính xác hơn
    forgot_link = pg.locator(".smart__forget__link")
    expect(forgot_link).to_be_visible()
    expect(forgot_link).to_have_text("パスワードを忘れた場合") # Xác minh nội dung văn bản của liên kết

def test_login_28(pg):
    forgot_link = pg.locator(".smart__forget__link")
    forgot_link.click()
    pg.wait_for_load_state("networkidle") # Chờ trang mới tải xong

    # Xác minh việc chuyển hướng đến trang đặt lại mật khẩu
    expect(pg).to_have_url(re.compile(r".*/reset.*")) # Regex linh hoạt hơn cho URL

    #expect(pg.locator("text=パスワード再設定")).to_be_visible()


# =============================
# RUN ALL TESTS + REPORT
# =============================
if __name__ == "__main__":
    start_time = time.time()
    results = []

    # Tạo folder report nếu chưa có
    os.makedirs("test_reports/screenshots", exist_ok=True)

    # Lấy danh sách test functions
    test_functions = [
        (name, func) for name, func in globals().items()
        if callable(func) and name.startswith("test_login_")
    ]
    # Sắp xếp theo số thứ tự để chạy đúng kịch bản
    test_functions.sort(key=lambda x: int(x[0].split("_")[-1]))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        for name, test_func in test_functions:
            print(f"Running {name}...", end=" ", flush=True)
            page = context.new_page()
            
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
                # Chụp screenshot khi có lỗi
                
                page.screenshot(path=f"test_reports/screenshots/{name}.png")
                with open(f"test_reports/screenshots/{name}_error.txt", "w", encoding="utf-8") as f:
                    f.write(traceback.format_exc())
            
            results.append({
                "name": name,
                "status": status,
                "error": error_msg
            })
            page.close()

        browser.close()


    # =============================
    # EXPORT REPORT
    # =============================
    report_path = "test_reports/execution_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"TEST EXECUTION REPORT - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Duration: {round(time.time() - start_time, 2)} seconds\n")
        f.write("-" * 50 + "\n")

        for res in results:
            line = f"[{res['status']}] {res['name']}"
            if res['error']:
                line += f" - Error: {res['error']}"
            f.write(line + "\n")

    print(f"\n✨ Report generated at: {os.path.abspath(report_path)}")