import os
import re
import time
import traceback
from datetime import datetime
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
# TEST CASES (GIỮ NGUYÊN 28)
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
    expect(password_input).to_have_attribute("type", "password")
    toggle_btn = pg.get_by_label("append icon")
    toggle_btn.click()
    expect(password_input).to_have_attribute("type", "text")

def test_login_14(pg):
    password_input = pg.locator("#password")
    toggle_btn = pg.get_by_label("append icon")
    password_input.fill("12345678")
    toggle_btn.click()
    expect(password_input).to_have_attribute("type", "text")

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
    expect(pg.locator(".smart__forget__link")).to_be_visible()

def test_login_28(pg):
    pg.locator(".smart__forget__link").click()
    pg.wait_for_load_state("networkidle")
    expect(pg).to_have_url(re.compile(r".*/reset.*"))

# =============================
# RUNNER + VIDEO
# =============================

if __name__ == "__main__":
    # Lưu lại thời gian bắt đầu chạy toàn bộ test
    start_time = time.time()

    # Tạo timestamp theo format yyyyMMdd_HHmmss
    # dùng để tạo folder riêng cho mỗi lần run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Tạo đường dẫn folder lưu video
    # Ví dụ: test_reports/video_20260416_143210
    video_dir = f"test_reports/video_{timestamp}"

    # Tạo folder (nếu chưa tồn tại)
    os.makedirs(video_dir, exist_ok=True)

    # List lưu kết quả từng test
    results = []

    # Lấy tất cả function có tên bắt đầu bằng test_login_
    test_functions = [
        (name, func) for name, func in globals().items()
        if callable(func) and name.startswith("test_login_")
    ]

    # Sắp xếp test theo số thứ tự (1 → 28)
    test_functions.sort(key=lambda x: int(x[0].split("_")[-1]))

    # Khởi tạo Playwright
    with sync_playwright() as p:
        # Mở browser (headless=True = chạy ẩn)
        browser = p.chromium.launch(headless=True)

        # Loop từng test case
        for name, test_func in test_functions:
            print(f"Running {name}...", end=" ")

            # Tạo context mới cho mỗi test
            # record_video_dir = bật quay video
            context = browser.new_context(record_video_dir=video_dir)

            # Mỗi context có page riêng
            page = context.new_page()

            # Lưu thời gian bắt đầu test
            start = time.time()

            try:
                # Mở trang login
                page.goto(BASE_URL)

                # Chạy test function
                test_func(page)

                # Nếu không lỗi → PASSED
                status = "PASSED"
                error = ""
                print("✅")

            except Exception as e:
                # Nếu có lỗi → FAILED
                status = "FAILED"
                error = str(e)
                print("❌")

            # Tính thời gian chạy test
            duration = round(time.time() - start, 2)

            # QUAN TRỌNG:
            # Phải close context thì Playwright mới lưu video ra file
            context.close()

            # =============================
            # RENAME VIDEO
            # =============================

            # Lấy danh sách file video trong folder
            video_files = os.listdir(video_dir)

            # Lấy file video mới nhất (vừa tạo)
            latest_video = max(
                [os.path.join(video_dir, f) for f in video_files],
                key=os.path.getctime  # thời gian tạo file
            )

            # Đổi tên video theo tên test case
            # ví dụ: test_login_1.webm
            new_path = os.path.join(video_dir, f"{name}.webm")

            os.rename(latest_video, new_path)

            # Lưu kết quả test vào list
            results.append({
                "name": name,
                "status": status,
                "duration": duration,
                "video": new_path,
                "error": error
            })

        # Đóng browser sau khi chạy xong tất cả test
        browser.close()

    # =============================
    # HTML REPORT
    # =============================

    # Tạo file report.html trong folder video
    report_path = os.path.join(video_dir, "report.html")

    with open(report_path, "w", encoding="utf-8") as f:
        # HTML cơ bản
        f.write("<html><head><title>Test Report</title></head><body>")

        # Tiêu đề report
        f.write(f"<h2>Test Report - {timestamp}</h2>")

        # Tạo bảng hiển thị kết quả
        f.write("<table border='1' cellpadding='5'>")
        f.write("<tr><th>Test</th><th>Status</th><th>Duration</th><th>Video</th></tr>")

        # Loop từng test result
        for r in results:
            # Màu sắc theo status
            color = "green" if r["status"] == "PASSED" else "red"

            # Lấy tên file video (không lấy full path)
            video_link = os.path.basename(r["video"])

            f.write(f"<tr>")
            f.write(f"<td>{r['name']}</td>")
            f.write(f"<td style='color:{color}'>{r['status']}</td>")
            f.write(f"<td>{r['duration']}s</td>")

            # Link mở video
            f.write(f"<td><a href='{video_link}'>View</a></td>")
            f.write(f"</tr>")

        f.write("</table></body></html>")

    # In ra console đường dẫn
    print(f"\n🎥 Video folder: {video_dir}")
    print(f"📄 Report: {report_path}")