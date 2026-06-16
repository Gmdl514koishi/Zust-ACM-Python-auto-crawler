import time
from typing import List, Optional
from playwright.sync_api import BrowserContext

from crawler.pipelines.cookie_pipeline import save_cookies_to_json, validate_cookies
from crawler.utils.cookie_utils import playwright_cookies_to_dict
from crawler.utils.logging_utils import setup_logging

# 配置日志
logger = setup_logging()

def wait_for_required_cookies(
    context: BrowserContext,
    page,
    url: str,
    required_cookies: Optional[List[str]] = None,
    max_retries: int = 5,
    retry_delay: int = 2
) -> bool:
    """
    等待并获取必需的登录 Cookie, 支持自动刷新页面直到获取所有必需的 Cookie
    
    :param context: Playwright BrowserContext 对象
    :param page: Playwright Page 对象
    :param url: 目标网址，用于获取相关域名的 Cookie
    :param required_cookies: 必需的 Cookie 名称列表
    :param max_retries: 最大重试次数
    :param retry_delay: 每次重试间隔（秒）
    :return: 是否成功获取所有必需的 Cookie
    """
    if required_cookies is None:
        required_cookies = ['access_token', 'id_token', 'post-login-redirect-url', 'refresh_token']
    
    for attempt in range(max_retries):
        # 等待页面完全加载
        page.wait_for_load_state('networkidle')
        time.sleep(retry_delay)  # 额外等待让 cookie 完全设置
        
        # 获取当前的 cookie（包括多个相关域名）
        # webvpn_username 的 Domain 是 .zust.edu.cn，需要显式指定域名才能获取
        playwright_cookies = context.cookies(url)
        cookies = playwright_cookies_to_dict(playwright_cookies)
        
        # 获取当前已有的 cookie 名称列表
        current_cookie_names = [cookie.get('name') for cookie in cookies if cookie.get('name')]
        
        logger.info(f"第 {attempt + 1}/{max_retries} 次尝试获取 Cookie")
        logger.info(f"当前已获取的 Cookie: {current_cookie_names}")
        
        # 检查是否包含所有必需的 cookie
        missing_cookies = [name for name in required_cookies if name not in current_cookie_names]
        
        if not missing_cookies:
            # 所有必需的 cookie 都已获取到
            logger.info("已获取所有必需的 Cookie, 保存中...")
            if validate_cookies(cookies):
                save_cookies_to_json(cookies)
                logger.info(f"已保存 Cookie(第 {attempt + 1} 次尝试)")
            else:
                logger.warning("Cookie 验证失败，未保存")
            return True
        else:
            logger.info(f"缺少以下必需的 Cookie: {missing_cookies}")
        
        # 如果还没有获取所有必需的 cookie，且不是最后一次尝试，刷新页面
        if attempt < max_retries - 1:
            logger.info("刷新页面以获取更多 Cookie...")
            page.reload()
        else:
            # 最后一次尝试，保存当前获取到的 cookie（即使不完整）
            logger.warning("已达到最大重试次数，保存当前获取到的 Cookie")
            if validate_cookies(cookies):
                save_cookies_to_json(cookies)
                logger.info(f"已保存 Cookie(第 {attempt + 1} 次尝试)")
            else:
                logger.warning("Cookie 验证失败，未保存")
            return False
    
    return False