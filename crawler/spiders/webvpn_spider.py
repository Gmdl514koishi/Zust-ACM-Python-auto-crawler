from crawler.pipelines.cookie_pipeline import save_cookies_to_json
from crawler.utils.config_utils import get_webvpn_password_from_env, get_webvpn_username_from_env
from crawler.utils.browser_utils import click_element
from crawler.utils.browser_utils import fill_element
from crawler.utils.selector_utils import load_selectors
from playwright.sync_api import Page, BrowserContext
from venv import logger

SELECTORS = load_selectors(form_type='WEBVPN')

def fill_webvpn_username(page: Page) -> bool:
    """
    在登录页面自动填入 WebVPN 用户名
    
    :param page: Playwright page 对象
    :return: 是否成功填写 WebVPN 用户名
    """
    user_webvpn_username = get_webvpn_username_from_env()
    if not user_webvpn_username:
        logger.error("未获取到 WebVPN 用户名配置")
        return False
    
    # 使用 fill_element 函数填入 WebVPN 用户名
    if not fill_element(page, SELECTORS['username_input'], user_webvpn_username, timeout=5000):
        logger.error("未找到 WebVPN 用户名输入框")
        return False
    
    logger.info(f"已填写 WebVPN 用户名")
    return True

def fill_webvpn_password(page: Page) -> bool:
    """
    在登录页面自动填入 WebVPN 密码
    
    :param page: Playwright page 对象
    :return: 是否成功填写 WebVPN 密码
    """
    user_webvpn_password = get_webvpn_password_from_env()
    if not user_webvpn_password:
        logger.error("未获取到 WebVPN 密码配置")
        return False
    
    # 使用 fill_element 函数填入 WebVPN 密码
    if not fill_element(page, SELECTORS['password_input'], user_webvpn_password, timeout=5000):
        logger.error("未找到 WebVPN 密码输入框")
        return False
    
    logger.info(f"已填写 WebVPN 密码")
    return True

def click_webvpn_login_button(page: Page, context: BrowserContext, target_url: str) -> str | None:
    """
    在登录页面自动点击 WebVPN 登录按钮，等待重定向后保存并返回 webvpn_username cookie
    
    :param page: Playwright page 对象
    :param context: Playwright context 对象(用于获取 cookie)
    :param target_url: 目标重定向 URL
    :return: webvpn_username cookie 值，失败返回 None
    """
    if not click_element(page, SELECTORS['login_submit'], timeout=10000):
        logger.error("未找到 WebVPN 登录按钮")
        return None
    
    logger.info("已点击 WebVPN 登录按钮，等待登录完成...")
    
    # 等待页面完全加载
    page.wait_for_load_state('networkidle')
    
    # 获取所有 cookie
    cookies = context.cookies()
    
    # 查找 webvpn_username cookie
    webvpn_username_cookie = None
    webvpn_username_value = None
    cookies_to_save = []
    
    for cookie in cookies:
        cookies_to_save.append({
            'name': cookie.get('name'),
            'value': cookie.get('value'),
            'domain': cookie.get('domain'),
            'path': cookie.get('path'),
            'expires': cookie.get('expires'),
            'httpOnly': cookie.get('httpOnly'),
            'secure': cookie.get('secure'),
            'sameSite': cookie.get('sameSite'),
        })
        
        if cookie.get('name') == 'webvpn_username':
            webvpn_username_cookie = cookie
            webvpn_username_value = cookie.get('value')
            display_value = webvpn_username_value[:50] if webvpn_username_value else ''
            logger.info(f"已获取 webvpn_username cookie")
    
    # 保存所有 cookie
    if cookies_to_save:
        save_cookies_to_json(cookies_to_save)
        logger.info(f"已保存 WebVPN Cookie, 共 {len(cookies_to_save)} 个")
    
    # 返回 webvpn_username 值
    if webvpn_username_value:
        return webvpn_username_value
    
    logger.warning("未找到 webvpn_username cookie")
    return None

def do_webvpn_login(page: Page, context: BrowserContext, target_url: str) -> str | None:
    """
    在登录页面自动完成 WebVPN 登录，等待重定向后返回 webvpn_username cookie
    
    :param page: Playwright page 对象
    :param context: Playwright context 对象(用于获取 cookie)
    :param target_url: 目标重定向 URL
    :return: webvpn_username cookie 值，失败返回 None
    """
    if not fill_webvpn_username(page):
        return None
    if not fill_webvpn_password(page):
        return None
    return click_webvpn_login_button(page, context, target_url)
