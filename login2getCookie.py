from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 必须 False，方便你手动登录
    context = browser.new_context()
    page = context.new_page()

    # 打开  登录页（或任意需要登录的页面）
    page.goto("https://sysxxh.henau.edu.cn/customer/index/index.html")

    print("请在打开的浏览器中完成登录，然后回到终端按 Enter")
    input()

    # 保存当前登录态
    context.storage_state(path="storage_state.json")
    print("登录状态已保存为 storage_state.json")

    browser.close()
