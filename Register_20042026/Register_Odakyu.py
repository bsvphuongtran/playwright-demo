import os
import re
import time
import traceback
from playwright.sync_api import Playwright, sync_playwright, expect, Page

# =============================
# CONFIG
# =============================
BASE_URL = "https://admin.odakyu.bravesoft.vn/login"
ACCOUNT_MGMT_URL = "https://admin.odakyu.bravesoft.vn/account-management"
EMAIL_LOGIN = "kimtran@bravesoft.com.vn"
PASSWORD_LOGIN = "brave0404"

VALID_EMAIL = "kimtran@bravesoft.com.vn"
VALID_PASSWORD = "brave0404"

EMAIL = "input[name=\"email\"]"
PASSWORD = "input[type='password']"
LOGIN_BTN = "button:has-text('ログイン')"

AUTH_FILE = "auth.json"

# =============================
# PREREQUISITE
# =============================
def setup_register_popup(page: Page):
    """Điều kiện tiên quyết: Login và mở popup 新規アカウント追加."""
    page.goto(BASE_URL)
    page.fill(EMAIL, VALID_EMAIL)
    page.fill(PASSWORD, VALID_PASSWORD)
    page.get_by_role("button", name="ログイン").click()
    expect(page.locator("div").filter(has_text=re.compile(r"^アカウント管理$"))).to_be_visible()


    # Cách khác:
    # page.goto("https://admin.odakyu.bravesoft.vn/login")
    # page.locator("input[name=\"email\"]").click()
    # page.locator("input[name=\"email\"]").fill("kimtran@bravesoft.com.vn")
    # page.locator("#password").click()
    # page.locator("#password").fill("brave0404")
    # page.get_by_role("button", name="ログイン").click()
    # expect(page.locator("div").filter(has_text=re.compile(r"^アカウント管理$"))).to_be_visible()

    page.get_by_role("button", name="新規追加").click()
    #expect(page.get_by_text("新規アカウント追加")).to_be_visible()


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



# def test_register_cancel_popup(page: Page):
#     setup_register_popup(page)
#     page.get_by_role("button", name="キャンセル").click()
#     expect(page.get_by_text("新規アカウント追加")).to_be_hidden()
#     expect(page.locator("div").filter(has_text=re.compile(r"^アカウント管理$"))).to_be_visible()

# =============================
# RUNNER
# =============================
def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        # Sử dụng storage_state nếu có để tăng tốc độ test
        storage = AUTH_FILE if os.path.exists(AUTH_FILE) else None
        context = browser.new_context(storage_state=storage)
    
        # test_list = [
        #     test_register_1,
        #     test_register_2,
        #     test_register_3,
        #     test_register_4,
        #     test_register_5, 
        #     test_register_cancel_popup
        # ]

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

        for name, test_func in test_functions:
            page = context.new_page()
            print(f"Running {name}...", end=" ")
            try:
                test_func(page)
                print("✅ PASSED")
            except Exception as e:
                print(f"❌ FAILED: {e}")
            page.close()

        browser.close()

if __name__ == "__main__":
    run_tests()