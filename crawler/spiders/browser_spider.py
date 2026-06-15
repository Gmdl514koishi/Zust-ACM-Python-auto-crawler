from crawler.utils.browser_utils import click_element, fill_element
from crawler.utils.config_utils import get_email_from_env
from playwright.sync_api import sync_playwright, Page, Browser
from crawler.pipelines.cookie_pipeline import load_cookies_from_json, save_cookies_to_json 

# 选择器常量
SELECTORS = {
    'login_button': 'button[data-slot="dropdown-menu-trigger"][data-sidebar="menu-button"]',
    'login_now_button': 'a:has-text("立即登录")',
    'email_input': 'input[name="p_email"], input[id="sign_up_sign_in_credentials_p_email"]',
    'continue_button': 'button[type="submit"][data-kinde-button="true"]',
    'verification_code_input': 'input[name="p_confirmation_code"], input[id="otp_code_p_confirmation_code"]'
}

def login(url: str) -> tuple[Page | None, Browser | None]:
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
            
            if not fill_email(page):
                print("ERROR: 填写邮箱失败")
                return None, None

            if not click_element(page, SELECTORS['email_input'], timeout=5000):
                print("ERROR: 未找到邮箱输入框")
                return None, None
            
            if not fill_verification_code(page):
                print("ERROR: 填写验证码失败")
                return None, None
            print("登录成功")
            
            # 等待登录完成，保存cookie
            page.wait_for_load_state('networkidle')
            save_cookies_to_json(context.cookies())
            print(f"已保存cookie")

            input("按任意键继续...")

            return page, browser
            
        except Exception as err:
            print(f"ERROR: {str(err)}")
            return None, None

def fill_email(page: Page) -> bool:
    """
    在登录页面自动填入邮箱
    
    :param page: Playwright page 对象
    """
    user_email = get_email_from_env()
    if not user_email:
        print("ERROR: 未获取到邮箱配置")
        return False

    # 使用 fill_element 函数填入邮箱
    if not fill_element(page, SELECTORS['email_input'], user_email, timeout=5000):
        print("ERROR: 未找到邮箱输入框")
        return False
    
    # 点击 Continue 按钮
    if not click_element(page, SELECTORS['continue_button'], timeout=5000):
        print("ERROR: 未找到 Continue 按钮")
        return False
    
    print(f"已填写邮箱: {user_email}")
    return True


def fill_verification_code(page: Page) -> bool:
    """
    从终端输入验证码并提交
    
    :param page: Playwright page 对象
    :return: 是否成功填写验证码
    """
    # 从终端获取验证码
    code = input("请输入验证码(6位数字): ").strip()
    
    if not code:
        print("ERROR: 验证码不能为空")
        return False
    
    # 检查验证码是否为6位数字
    # 后续重构：添加验证码格式校验逻辑
    if not code.isdigit() or len(code) != 6:
        print("ERROR: 验证码必须为6位数字")
        return False
    
    # 填入验证码
    if not fill_element(page, SELECTORS['verification_code_input'], code, timeout=5000):
        print("ERROR: 未找到验证码输入框")
        return False
    
    # 点击 Continue 按钮
    if not click_element(page, SELECTORS['continue_button'], timeout=5000):
        print("ERROR: 未找到 Continue 按钮")
        return False
    
    print(f"已提交验证码: {code}")
    return True
