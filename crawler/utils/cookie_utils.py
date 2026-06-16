import time
from crawler.pipelines.cookie_pipeline import load_cookies_from_json, save_cookies_to_json, validate_cookies
from crawler.utils.logging_utils import setup_logging
from typing import List, Dict, Any, Optional
from playwright.sync_api import BrowserContext

# 配置日志
logger = setup_logging()

def check_cookies_valid(cookie_names: Optional[List[str]] = None) -> bool:
    """
    检查指定的 Cookie 是否存在且有效
    
    :param cookie_names: 需要检查的 Cookie 名称列表，如果为 None 则检查所有 Cookie
    :return: 如果所有指定的 Cookie 都有效则返回 True, 否则返回 False
    """
    valid_cookies = {}
    existing_cookies = load_cookies_from_json()
    
    if not existing_cookies:
        logger.info("未找到已保存的 Cookie")
        return False
    
    for cookie in existing_cookies:
        cookie_name = cookie.get('name')
        cookie_value = cookie.get('value')
        
        if not cookie_name or not cookie_value:
            continue
        
        # 如果指定了需要检查的 Cookie 名称，只检查这些
        if cookie_names and cookie_name not in cookie_names:
            continue
        
        if cookie.get('expires') and cookie['expires'] > time.time():
            valid_cookies[cookie_name] = cookie_value
        display_value = cookie_value[:50] if cookie_value else ''
        logger.info(f"发现有效的 Cookie: {cookie_name} = {display_value}...")
    
    if not valid_cookies:
        logger.info("未找到有效的 Cookie")
        return False
    else:
        logger.info(f"共找到 {len(valid_cookies)} 个有效的 Cookie")
        return True

def playwright_cookies_to_dict(cookies: List[Any]) -> List[Dict[str, Any]]:
    """
    将 Playwright Cookie 对象列表转换为字典列表
    
    :param cookies: Playwright Cookie 对象列表
    :return: 字典列表
    """
    result = []
    for cookie in cookies:
        # Playwright Cookie 对象可以通过 __dict__ 或 as_dict() 转换
        if hasattr(cookie, 'as_dict'):
            result.append(cookie.as_dict())
        elif hasattr(cookie, '__dict__'):
            result.append(dict(cookie.__dict__))
        else:
            # 如果已经是字典
            result.append(dict(cookie))
    return result

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
    # 更新默认的 required_cookies 参数，包含所有必要的 Cookie
    if required_cookies is None:
        required_cookies = ['access_token', 'id_token', 'post-login-redirect-url', 'refresh_token', 'ac-state-key']
    
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
                save_cookies_to_json(cookies, merge=True)
                logger.info(f"已保存 Cookie(第 {attempt + 1} 次尝试)")
            else:
                logger.warning("Cookie 验证失败，未保存")
            return False
    
    return False