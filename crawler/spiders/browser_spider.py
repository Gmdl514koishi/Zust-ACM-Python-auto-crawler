from crawler.utils.browser_utils import click_element, fill_element
from crawler.utils.config_utils import get_email_from_env
from playwright.sync_api import sync_playwright, Page, Browser

# 选择器常量
SELECTORS = {
    'login_button': 'button[data-slot="dropdown-menu-trigger"][data-sidebar="menu-button"]',
    'login_now_button': 'a:has-text("立即登录")',
    'email_input': 'input[name="p_email"], input[id="sign_up_sign_in_credentials_p_email"]'
}

def click_login_button(url: str) -> tuple[Page | None, Browser | None]:
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
            page.goto(url)
            print(f"已打开: {url}")
            
            # 点击登录按钮
            if not click_element(page, SELECTORS['login_button'], timeout=10000):
                print("ERROR: 未找到登录按钮")
                return None, None

            # 点击"立即登录"按钮
            if not click_element(page, SELECTORS['login_now_button'], timeout=5000):
                print("ERROR: 未找到'立即登录'按钮")
                return None, None
            
            # 等待重定向
            page.wait_for_load_state('networkidle')
            login_url = page.url
            print(f"重定向完成: {login_url}")
            
            fill_email(page)
            
            # 5. 等待用户操作
            input("\n登录完成后按 Enter 键继续...")
            
            return page, browser
            
        except Exception as err:
            print(f"ERROR: {str(err)}")
            return None, None
        
def fill_email(page: Page) -> None:
    """
    在登录页面自动填入邮箱
    
    :param page: Playwright page 对象
    """
    user_email = get_email_from_env()
    if not user_email:
        print("ERROR: 未获取到邮箱配置")
        return
    
    # 使用 fill_element 函数填入邮箱
    if not fill_element(page, SELECTORS['email_input'], user_email, timeout=5000):
        print("ERROR: 未找到邮箱输入框")

