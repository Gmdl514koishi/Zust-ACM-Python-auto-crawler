from playwright.sync_api import sync_playwright

def click_login_button(url: str):
    """
    后台模式：先在后台完成点击和重定向，然后打开可视化浏览器让用户手动登录
    
    :param url: 目标网址
    :return: page, browser 对象（用于后续操作）
    """
    # ========== 阶段1：后台完成点击和重定向 ==========
    print("🔄 正在后台处理...")
    
    # 保存需要传递到可视化浏览器的数据
    login_url = None
    cookies_dict = []
    
    with sync_playwright() as p:
        # 后台浏览器（无头模式）
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3.1 Safari/605.1.15"
        )
        page = context.new_page()
        
        try:
            # 打开原始页面
            page.goto(url)
            
            # 点击登录按钮
            login_button = page.wait_for_selector(
                'button[data-slot="dropdown-menu-trigger"][data-sidebar="menu-button"]',
                timeout=10000
            )
            if login_button is None:
                print("❌ 错误: 未找到登录按钮")
                return None, None
            login_button.click()
            
            # 点击"立即登录"
            login_now_button = page.wait_for_selector('a:has-text("立即登录")', timeout=5000)
            if login_now_button is None:
                print("❌ 错误: 未找到'立即登录'按钮")
                return None, None
            login_now_button.click()
            
            # 等待重定向完成
            page.wait_for_load_state('networkidle')
            
            # 保存登录页面 URL
            login_url = page.url
            
            # 保存 Cookie
            cookies = context.cookies()
            cookies_dict = []
            for cookie in cookies:
                cookie_dict = dict(cookie)
                cookies_dict.append({
                    'name': cookie_dict.get('name', ''),
                    'value': cookie_dict.get('value', ''),
                    'domain': cookie_dict.get('domain', ''),
                    'path': cookie_dict.get('path', '/'),
                    'expires': cookie_dict.get('expires'),
                    'httpOnly': cookie_dict.get('httpOnly', False),
                    'secure': cookie_dict.get('secure', False),
                    'sameSite': cookie_dict.get('sameSite', 'Lax')
                })
            
            print(f"✅ 后台处理完成")
            
        except Exception as e:
            print(f"❌ 后台处理失败: {str(e)}")
            return None, None
        
        # with 语句结束，后台浏览器自动关闭
    
    # ========== 阶段2：打开可视化浏览器 ==========
    print(f"🌐 登录页面: {login_url}")
    print("🔓 正在打开浏览器，请手动登录...")
    
    # 启动新的 Playwright 实例（不使用 with）
    p = sync_playwright().start()
    
    # 创建可视化浏览器
    browser = p.chromium.launch(
        headless=False,
        args=['--start-maximized']
    )
    
    # 创建上下文并导入 Cookie
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3.1 Safari/605.1.15"
    )
    
    # 导入 Cookie
    if cookies_dict:
        context.add_cookies(cookies_dict)
    
    # 打开登录页面
    page = context.new_page()
    page.goto(login_url)
    
    # 等待用户操作
    input("\n登录完成后按 Enter 键继续...")
    
    return page, browser