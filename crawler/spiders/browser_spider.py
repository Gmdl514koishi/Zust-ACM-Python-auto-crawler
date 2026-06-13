from playwright.sync_api import sync_playwright

def click_login_button(url: str):
    """
    直接模式：直接启动可视化浏览器，完成点击和重定向后让用户登录
    
    :param url: 目标网址
    :return: page, browser 对象（用于后续操作）
    """
    print("正在启动浏览器...")
    
    with sync_playwright() as p:
        # 直接启动可视化浏览器
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3.1 Safari/605.1.15"
        )
        
        page = context.new_page()
        
        try:
            # 1. 打开原始页面
            page.goto(url)
            print(f"已打开: {url}")
            
            # 2. 点击登录按钮
            login_button = page.wait_for_selector(
                'button[data-slot="dropdown-menu-trigger"][data-sidebar="menu-button"]',
                timeout=10000
            )
            if login_button is None:
                print("ERROR: 未找到登录按钮")
                return None, None
            login_button.click()
            print("已点击登录按钮")
            
            # 3. 点击"立即登录"
            login_now_button = page.wait_for_selector('a:has-text("立即登录")', timeout=5000)
            if login_now_button is None:
                print("ERROR: 未找到'立即登录'按钮")
                return None, None
            login_now_button.click()
            print("已点击'立即登录'")
            
            # 4. 等待重定向完成
            page.wait_for_load_state('networkidle')
            login_url = page.url
            print(f"重定向完成: {login_url}")
            
            print(f"\n登录页面已准备好")
            print("请在浏览器中手动登录...")
            
            # 5. 等待用户操作
            input("\n登录完成后按 Enter 键继续...")
            
            return page, browser
            
        except Exception as e:
            print(f"发生错误: {str(e)}")
            return None, None