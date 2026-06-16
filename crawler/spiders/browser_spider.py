from crawler.pipelines.cookie_pipeline import load_cookies_from_json, validate_cookies, clean_expired_cookies
from crawler.pipelines.html_pipeline import save_html_to_html
from crawler.utils.logging_utils import setup_logging
from playwright.sync_api import sync_playwright

# 配置日志
logger = setup_logging()

def fetch_save_webpage(url: str, required_cookies: list[str], headless: bool = True) -> None:
    """
    使用 Playwright 携带 Cookie 登录并等待页面完全加载后爬取网页源代码
    
    :param url: 目标网址
    :param required_cookies: 必须包含的 Cookie 名称列表
    :param headless: 是否以无头模式运行浏览器，默认 True
    :return: None
    """
    # 定义需要的 Cookie 名称
    required_cookie_names = required_cookies
    
    # 加载并验证 Cookie
    cookies = load_cookies_from_json()
    if cookies:
        validate_cookies(cookies)
        clean_expired_cookies()
        
        # 过滤出需要的 Cookie
        filtered_cookies = [cookie for cookie in cookies if cookie.get('name') in required_cookie_names]
        cookies = filtered_cookies if filtered_cookies else None
    
    if not cookies:
        logger.error("没有有效的 Cookie, 无法爬取网页")
        return
    
    logger.info(f"正在使用 Playwright 爬取网页: {url}")
    logger.info(f"携带 {len(cookies)} 个 Cookie")
    
    # 转换 Cookie 为 Playwright 需要的格式
    playwright_cookies = []
    for cookie in cookies:
        playwright_cookie = {
            'name': cookie.get('name', ''),
            'value': cookie.get('value', ''),
        }
        # 添加可选字段
        if cookie.get('domain'):
            playwright_cookie['domain'] = cookie['domain']
        if cookie.get('path'):
            playwright_cookie['path'] = cookie['path']
        if cookie.get('expires'):
            playwright_cookie['expires'] = cookie['expires']
        if cookie.get('httpOnly') is not None:
            playwright_cookie['httpOnly'] = cookie['httpOnly']
        if cookie.get('secure') is not None:
            playwright_cookie['secure'] = cookie['secure']
        if cookie.get('sameSite'):
            playwright_cookie['sameSite'] = cookie['sameSite']
        playwright_cookies.append(playwright_cookie)
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=headless)
        
        # 创建新的浏览器上下文
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3.1 Safari/605.1.15"
        )
        
        # 添加 Cookie 到上下文
        context.add_cookies(playwright_cookies)
        logger.info("已添加 Cookie 到浏览器上下文")
        
        # 创建新页面
        page = context.new_page()
        
        try:
            # 导航到目标 URL
            logger.info(f"正在访问: {url}")
            page.goto(url, timeout=30000)
            
            # 等待页面完全加载
            logger.info("等待页面完全加载...")
            page.wait_for_load_state('networkidle', timeout=30000)
            logger.info("页面已完全加载")
            
            # 获取页面源代码
            webpage_source = page.content()
            logger.info(f"已获取页面源代码，长度: {len(webpage_source)} 字符")
            
            # 保存网页源代码
            save_html_to_html(webpage_source, filename=url)
            logger.info(f"网页 {url} 源代码爬取完成!")

            # input("[临时]按任意键继续...")
            
        except Exception as err:
            logger.error(f"爬取网页失败: {str(err)}")
            # 保存当前页面的 HTML 用于调试
            try:
                debug_html = page.content()
                save_html_to_html(debug_html, filename=f"{url}_error")
                logger.info("已保存错误页面的 HTML 用于调试")
            except:
                pass
        finally:
            # 关闭浏览器
            browser.close()