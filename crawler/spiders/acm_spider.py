from bs4 import BeautifulSoup
from crawler.pipelines.html_pipeline import save_html_to_html
from crawler.pipelines.cookie_pipeline import load_cookies_from_json, validate_cookies, clean_expired_cookies
from crawler.spiders.intellijudge_spider import do_intellijudge_login
from crawler.spiders.webvpn_spider import do_webvpn_login
from crawler.utils.browser_utils import click_element
from crawler.utils.cookie_utils import wait_for_required_cookies, check_cookies_valid
from crawler.utils.logging_utils import setup_logging
from crawler.utils.selector_utils import load_selectors
from playwright.sync_api import sync_playwright, Page, Browser

# 配置日志
logger = setup_logging()

# 选择器常量
SELECTORS = load_selectors(form_type='ACM')

def find_login_button(html: str) -> dict:
    """
    从 HTML 中查找登录按钮元素。
    
    :param html: 包含登录按钮的 HTML 字符串
    :return: 包含按钮信息的字典，包含 'found'（是否找到）和 'message'（登录状态信息）
    """
    soup = BeautifulSoup(html, 'html.parser')
    login_button = soup.find(
        'button', 
        attrs={
            'data-slot': 'dropdown-menu-trigger',
            'data-sidebar': 'menu-button',
        }
    )

    button_info = {
        'found': False,
        'is_log_in': False,
        'message': '未找到按钮',
    }
    if not login_button:
        return button_info

    button_info['found'] = True
    button_txt = login_button.get_text(strip=True)
    is_logged_out: bool = '未登录' in button_txt or '请先登陆账号' in button_txt
    button_info['is_log_in'] = False if is_logged_out else True
    button_info['message'] = '未登录' if is_logged_out else '已登录'
    return button_info

def login(url: dict[str, str], headless: bool = True) -> tuple[Page | None, Browser | None]:
    """
    完整登录流程：先进行 WebVPN 登录，再进行 IntelliJudge 登录
    
    :param url: 包含登录网址字典，包含 'webvpn_username' 和 'root' 键
    :return: page, browser 对象（用于后续操作）
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=['--start-maximized']
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3.1 Safari/605.1.15"
        )
        
        page = context.new_page()

        try:
            # Step 1: 检查 webvpn_username cookie 是否有效
            valid_cookies = check_cookies_valid(['_webvpn_key', 'webvpn_username'])
            
            if valid_cookies == True:
                # Cookie 有效，直接访问主页面
                logger.info("WebVPN Cookie 有效，跳过登录步骤")
            else:
                # Cookie 无效或不存在，进行 WebVPN 登录
                logger.info(f"正在打开 WebVPN 登录页面: {url['webvpn_username']}")
                page.goto(url['webvpn_username'])
                
                logger.info("开始 WebVPN 登录...")
                webvpn_username_value = do_webvpn_login(page, context, url['root'])
                if not webvpn_username_value:
                    logger.error("WebVPN 登录失败")
                    return None, None
                logger.info(f"WebVPN 登录成功")

            # Step 2: 访问主页面（设置较短超时，不等待完全加载）
            logger.info(f"正在打开主页面: {url['root']}")
            page.goto(url['root'], timeout=15000)  # 15秒超时
            
            # Step 3: 等待登录按钮出现并点击
            logger.info("等待登录按钮出现...")
            try:
                page.wait_for_selector(SELECTORS['login_button'], timeout=20000)
                logger.info("登录按钮已出现")
            except Exception as err:
                error_msg = f"等待登录按钮超时，当前 URL: {page.url}, 错误: {str(err)}"
                logger.error(error_msg)
                return None, None
            
            if not click_element(page, SELECTORS['login_button'], timeout=10000):
                logger.error("未找到登录按钮")
                return None, None

            # Step 4: 点击"立即登录"按钮
            if not click_element(page, SELECTORS['login_now_button'], timeout=5000):
                logger.error("未找到'立即登录'按钮")
                return None, None
            
            # Step 5: 等待重定向
            page.wait_for_load_state('networkidle')
            login_url = page.url
            logger.info(f"重定向完成: {login_url}")
            
            # Step 6: IntelliJudge 登录
            logger.info("开始 IntelliJudge 登录...")
            if not do_intellijudge_login(page):
                logger.error("IntelliJudge 登录失败")
                return None, None

            # Step 7: 等待页面重定向回主页面
            root_url: str = url['root'] 
            try:
                logger.info(f"等待页面重定向到: {root_url}")
                page.wait_for_url(root_url, timeout=30000)
                logger.info(f"已成功重定向到: {root_url}")
            except Exception as err:
                error_msg = f"等待重定向超时，当前 URL: {page.url}, 错误: {str(err)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Step 8: 等待并获取必需的登录 Cookie
            required_cookies = ['access_token', 'id_token', 'post-login-redirect-url', 'refresh_token']
            if not wait_for_required_cookies(context, page, url['root'], required_cookies):
                logger.warning("未能获取所有必需的 Cookie")
            
            logger.info("登录流程完成")
            return page, browser
            
        except Exception as err:
            logger.error(f"登录过程出错: {str(err)}")
            return None, None
