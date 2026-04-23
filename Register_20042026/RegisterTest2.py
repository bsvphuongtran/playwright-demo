import json
import os
import re
from playwright.sync_api import sync_playwright, expect, Page, BrowserContext

# =============================
# CONFIG
# =============================
ACCOUNT_MGMT_URL = "https://admin.odakyu.bravesoft.vn/account-management"
AUTH_FILE = "auth.json"
TOKEN_FILE = "token.json"


def ensure_login():
    """Đảm bảo đã login và có token/session trước khi chạy test Register."""
    from Login import run_login

    if not os.path.exists(AUTH_FILE) or not os.path.exists(TOKEN_FILE):
        print("⚠️ Thiếu auth/token file. Đang thực hiện login để khởi tạo...")
        run_login(headless=False)


def load_token_state() -> dict:
    if not os.path.exists(TOKEN_FILE):
        return {"localStorage": {}, "sessionStorage": {}}
    with open(TOKEN_FILE, "r", encoding="utf-8") as token_file:
        return json.load(token_file)


def apply_token_to_context(context: BrowserContext, token_state: dict):
    local_storage = token_state.get("localStorage", {})
    session_storage = token_state.get("sessionStorage", {})

    context.add_init_script(
        """
        ({ localStorageData, sessionStorageData }) => {
            for (const [key, value] of Object.entries(localStorageData || {})) {
                window.localStorage.setItem(key, value);
            }
            for (const [key, value] of Object.entries(sessionStorageData || {})) {
                window.sessionStorage.setItem(key, value);
            }
        }
        """,
        {"localStorageData": local_storage, "sessionStorageData": session_storage},
    )


def login_on_current_page(page: Page):
    """Đăng nhập trực tiếp trên page hiện tại khi bị redirect về login."""
    from Login import (
        BASE_URL,
        EMAIL,
        PASSWORD,
        LOGIN_BTN,
        VALID_EMAIL,
        VALID_PASSWORD,
    )

    page.goto(BASE_URL)
    page.fill(EMAIL, VALID_EMAIL)
    page.fill(PASSWORD, VALID_PASSWORD)
    page.locator(LOGIN_BTN).click()
    page.wait_for_url(re.compile(r".*/account-management.*"))

    # Cập nhật lại session/token để những lần chạy sau có thể tái sử dụng.
    page.context.storage_state(path=AUTH_FILE)
    token_state = page.evaluate(
        """() => ({
            localStorage: { ...window.localStorage },
            sessionStorage: { ...window.sessionStorage }
        })"""
    )
    with open(TOKEN_FILE, "w", encoding="utf-8") as token_file:
        json.dump(token_state, token_file, ensure_ascii=False, indent=2)


def open_register_popup(page: Page):
    """Mở popup 新規アカウント追加 bằng nhiều selector fallback để giảm flaky."""
    button_candidates = [
        page.get_by_role("button", name="新規追加"),
        page.locator("button:has-text('新規追加')"),
        page.get_by_text("新規追加"),
    ]

    clicked = False
    for button in button_candidates:
        target = button.first
        try:
            target.scroll_into_view_if_needed(timeout=8000)
            target.click(timeout=8000)
            clicked = True
            break
        except Exception:
            continue

    if not clicked:
        raise AssertionError("Không tìm/click được button '新規追加' trên trang account-management.")

    popup_candidates = [
        page.get_by_text("新規アカウント追加"),
        page.locator("text=新規アカウント追加"),
    ]
    for popup in popup_candidates:
        try:
            expect(popup.first).to_be_visible(timeout=10000)
            return
        except Exception:
            continue

    raise AssertionError("Không mở được popup '新規アカウント追加' sau khi click 新規追加.")


def is_login_page(page: Page) -> bool:
    if "/login" in page.url:
        return True
    try:
        return page.locator("input[name='email']").first.is_visible(timeout=1500)
    except Exception:
        return False


def ensure_authenticated_page(page: Page):
    page.goto(ACCOUNT_MGMT_URL, wait_until="domcontentloaded")
    if is_login_page(page):
        login_on_current_page(page)
        page.goto(ACCOUNT_MGMT_URL, wait_until="domcontentloaded")

    if is_login_page(page):
        raise AssertionError("Không thể xác thực phiên login trước khi chạy testcase Register.")


def setup_register_popup(page: Page):
    """Điều kiện tiên quyết: đã login, vào account-management, mở popup 新規アカウント追加."""
    ensure_authenticated_page(page)

    page.wait_for_url(re.compile(r".*/account-management.*"), timeout=15000)
    page.wait_for_load_state("domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        # Một số request polling chạy liên tục nên networkidle có thể timeout.
        pass

    if is_login_page(page):
        ensure_authenticated_page(page)

    open_register_popup(page)


# =============================
# TEST CASES
# =============================
def test_register_1(page: Page):
    setup_register_popup(page)
    #assert "/account-management" in page.url
    expect(page).to_have_url(re.compile(r".*/account-management.*"))

def test_register_2(page: Page):
    setup_register_popup(page)
    expect(page.get_by_text("新規アカウント追加")).to_be_visible()

def test_register_3(page: Page):
    setup_register_popup(page)
    #expect(page.get_by_text("アカウント名 * （255文字以内）")).to_be_visible()
    expect(page.get_by_text(re.compile(r"アカウント名\s*\*\s*（255文字以内）"))).to_be_visible()

def test_register_4(page: Page):
    setup_register_popup(page)
    page.locator("input[name=\"userName\"]").fill("Test01")
    expect(page.locator("input[name=\"userName\"]")).to_have_value("Test01")

def test_register_5(page: Page):
    setup_register_popup(page)
    expect(page.get_by_text(re.compile(r"メールアドレス\s*\*\s*"))).to_be_visible()

def test_register_6(page: Page):
    setup_register_popup(page)
    page.locator("input[name=\"email\"]").fill("phuongtest111@gmail.com")
    expect(page.locator("input[name=\"email\"]")).to_have_value("phuongtest111@gmail.com")

def test_register_7(page: Page):
    setup_register_popup(page)
    #expect(page.get_by_text(re.compile(r"アカウント名\s*\*\s*（255文字以内）"))).to_be_visible()
    expect(page.get_by_text(re.compile(r"パスワード\s*\*\s*（半角英数字 8文字以上32文字以内）"))).to_be_visible()

def test_register_8(page: Page):
    setup_register_popup(page)
    expect(page.locator("input[name=\"password\"]")).to_have_attribute("placeholder", "**********")

def test_register_9(page: Page):
    setup_register_popup(page)
    page.get_by_role("textbox", name="**********").fill("Password123!")
    expect(page.get_by_role("textbox", name="**********")).to_have_value("Password123!")

def test_register_10(page: Page):
    setup_register_popup(page)
    expect(page.locator("form")).to_contain_text("権限 *")
    expect(page.get_by_role("combobox").nth(1)).to_be_visible()
    expect(page.get_by_role("combobox").nth(1)).to_have_text("")

def test_register_11(page: Page):
    setup_register_popup(page)
    page.get_by_role("combobox").nth(1).click()
    page.locator("span").filter(has_text="マスター管理者").click()
    expect(page.get_by_role("combobox").filter(has_text="マスター管理者")).to_be_visible()

def test_register_12(page: Page):
    setup_register_popup(page)
    page.get_by_role("combobox").nth(1).click()
    page.get_by_role("option", name="テナント管理者").click()
    expect(page.get_by_role("combobox").filter(has_text="テナント管理者")).to_be_visible()

def test_register_13(page: Page):
    setup_register_popup(page)
    page.get_by_role("combobox").nth(1).click()
    page.locator("span").filter(has_text="マスター管理者").click()
    expect(page.get_by_role("combobox").filter(has_text="マスター管理者")).to_be_visible()
    expect(page.get_by_role("combobox").nth(1)).not_to_contain_text("テナント管理者")
    page.get_by_role("combobox").filter(has_text="マスター管理者").click()
    page.get_by_role("option", name="テナント管理者").click()
    expect(page.get_by_role("combobox").filter(has_text="テナント管理者")).to_be_visible()
    expect(page.get_by_role("combobox").nth(1)).not_to_contain_text("マスター管理者")

def test_register_14(page: Page):
    setup_register_popup(page)
    page.get_by_role("combobox").nth(1).click()
    page.locator("span").filter(has_text="マスター管理者").click()
    expect(page.locator("form")).not_to_contain_text("チケット組成時のポイント付与パラメータの変更権限 *")
    page.get_by_role("combobox").nth(1).click()
    page.get_by_role("option", name="テナント管理者").click()
    expect(page.locator("form")).to_contain_text("チケット組成時のポイント付与パラメータの変更権限 *")
    expect(page.get_by_text("有")).to_be_visible()
    expect(page.get_by_text("無")).to_be_visible()

def test_register_15(page: Page):
    setup_register_popup(page)
    page.get_by_role("combobox").nth(1).click()
    page.get_by_role("option", name="テナント管理者").click()
    
    page.locator("#authority1").check()
    expect(page.locator("#authority1")).to_be_checked()

def test_register_16(page: Page):
    setup_register_popup(page)
    page.get_by_role("combobox").nth(1).click()
    page.get_by_role("option", name="テナント管理者").click()
    
    page.locator("#authority2").check()
    expect(page.locator("#authority2")).to_be_checked()

def test_register_17(page: Page):
    setup_register_popup(page)
    page.get_by_role("combobox").nth(1).click()
    page.get_by_role("option", name="テナント管理者").click()

    page.locator("#authority1").check()
    expect(page.locator("#authority1")).to_be_checked()
    expect(page.locator("#authority2")).not_to_be_checked()
    
    page.locator("#authority2").check()
    expect(page.locator("#authority2")).to_be_checked()
    expect(page.locator("#authority1")).not_to_be_checked()



def run_tests():
    ensure_login()
    token_state = load_token_state()

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(storage_state=AUTH_FILE)
        apply_token_to_context(context, token_state)

        # Kiểm tra session/token có hiệu lực.
        check_page = context.new_page()
        check_page.goto(ACCOUNT_MGMT_URL)
        if "/login" in check_page.url:
            print("🔴 Session/token hết hạn. Đăng nhập lại...")
            check_page.close()
            context.close()
            from Login import run_login

            run_login(headless=False)
            token_state = load_token_state()
            context = browser.new_context(storage_state=AUTH_FILE)
            apply_token_to_context(context, token_state)
        else:
            check_page.close()

        # Lấy tất cả function có tên bắt đầu bằng test_register_
        test_functions = [
            (name, func) for name, func in globals().items()
            if callable(func) and name.startswith("test_register_")
        ]

        # Sắp xếp test theo số thứ tự để chạy đúng trình tự kịch bản
        def get_test_num(item):
            try: return int(item[0].split("_")[-1])
            except: return 999
            
        test_functions.sort(key=get_test_num)


        for test in test_functions:
            page = context.new_page()
            print(f"Running {test.__name__}...", end=" ")
            try:
                test(page)
                print("✅ PASSED")
            except Exception as ex:
                print(f"❌ FAILED: {ex}")
            finally:
                page.close()

        context.close()
        browser.close()

if __name__ == "__main__":
    run_tests()