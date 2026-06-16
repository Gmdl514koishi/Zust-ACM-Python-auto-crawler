from bs4 import BeautifulSoup
from crawler.pipelines.html_pipeline import save_html_to_html
from crawler.pipelines.cookie_pipeline import load_cookies_from_json, validate_cookies, clean_expired_cookies
from crawler.spiders.intellijudge_spider import do_intellijudge_login
from crawler.spiders.webvpn_spider import do_webvpn_login
from crawler.utils.browser_utils import click_element
from crawler.utils.cookie_utils import wait_for_required_cookies
from crawler.utils.logging_utils import setup_logging
from crawler.utils.request_utils import fetch_webpage, check_webpage_source
from crawler.utils.selector_utils import load_selectors
from playwright.sync_api import sync_playwright, Page, Browser

# 配置日志
logger = setup_logging()

# 选择器常量
SELECTORS = load_selectors(form_type='ACM_login_inputs')

def fetch_save_webpage(url: str) -> None:
    """
    爬取并保存网页源代码
    
    :param url: 目标网址
    :return: None
    """
    # 加载并验证 Cookie
    cookies = load_cookies_from_json()
    if cookies:
        validate_cookies(cookies)
        clean_expired_cookies()

    html: str = fetch_webpage(url, cookies=cookies)
    webpage_source: str = check_webpage_source(html)
    save_html_to_html(webpage_source, filename=url)
    logger.info(f"网页 {url} 源代码爬取完成!")


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

def login(url: dict[str, str]) -> tuple[Page | None, Browser | None]:
    """
    完整登录流程：先进行 WebVPN 登录，再进行 IntelliJudge 登录
    
    :param url: 包含登录网址字典，包含 'webvpn_username' 和 'root' 键
    :return: page, browser 对象（用于后续操作）
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3.1 Safari/605.1.15"
        )
        
        page = context.new_page()

        try:
            # Step 1: WebVPN 登录
            logger.info(f"正在打开 WebVPN 登录页面: {url['webvpn_username']}")
            page.goto(url['webvpn_username'])
            
            logger.info("开始 WebVPN 登录...")
            webvpn_username_value = do_webvpn_login(page, context, url['root'])
            if not webvpn_username_value:
                logger.error("WebVPN 登录失败")
                return None, None
            logger.info(f"WebVPN 登录成功, webvpn_username: {webvpn_username_value}...")

            # Step 2: 访问主页面
            logger.info(f"正在打开主页面: {url['root']}")
            page.goto(url['root'])

            # Step 3: 点击登录按钮
            if not click_element(page, SELECTORS['ACM_login_buttons']['login_button'], timeout=10000):
                logger.error("未找到登录按钮")
                return None, None

            # Step 4: 点击"立即登录"按钮
            if not click_element(page, SELECTORS['ACM_login_buttons']['login_now_button'], timeout=5000):
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
            
            # Step 8: 等待并获取必需的登录 Cookie（包括 webvpn_username）
            required_cookies = ['access_token', 'id_token', 'post-login-redirect-url', 'refresh_token', 'webvpn_username']
            if not wait_for_required_cookies(context, page, url['root'], required_cookies):
                logger.warning("未能获取所有必需的 Cookie")
            
            logger.info("登录流程完成")
            return page, browser
            
        except Exception as err:
            logger.error(f"登录过程出错: {str(err)}")
            return None, None
