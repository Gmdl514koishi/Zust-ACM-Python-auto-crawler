import logging
import requests
from requests.cookies import RequestsCookieJar
from typing import Optional, List, Dict, Any

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

headers: Dict[str, str] = {
    "User-Agent": "ZUST-ACM-Crawler/1.0 (+https://github.com/Gmdl514koishi/Zust-ACM-Python-auto-crawler)",
    "From": "1251004020"
}

def cookies_to_dict(cookies: Optional[List[Dict[str, Any]]]) -> RequestsCookieJar:
    """
    将 Playwright 格式的 cookie 列表转换为 requests 可用的 RequestsCookieJar
    
    保留完整的 Cookie 属性: name, value, domain, path, secure, httpOnly, expires
    
    :param cookies: Playwright 获取的 cookie 列表，可为 None
    :return: requests 可用的 RequestsCookieJar 对象
    """
    jar = RequestsCookieJar()
    
    if not cookies:
        logger.debug("未提供 Cookie，返回空的 RequestsCookieJar")
        return jar
    
    for i, cookie in enumerate(cookies):
        try:
            # 验证必要字段
            if 'name' not in cookie or 'value' not in cookie:
                logger.warning(f"跳过第 {i} 个 Cookie：缺少 name 或 value 字段")
                continue
            
            jar.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie.get('domain'),
                path=cookie.get('path', '/'),
                secure=cookie.get('secure', False),
                expires=cookie.get('expires'),
                rest={'HttpOnly': cookie.get('httpOnly', False)}
            )
        except Exception as err:
            logger.error(f"处理第 {i} 个 Cookie 失败: {str(err)}")
    
    logger.debug(f"成功转换 {len(jar)} 个 Cookie")
    return jar


def fetch_webpage(url: str, cookies: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    获取网页源代码，支持带完整 cookie 访问

    :param url: 目标网址
    :param cookies: Cookie 列表 (Playwright 格式)，可选
    :return: 网页源代码
    """
    try:
        # 如果提供了 cookie，转换为 requests 可用的格式
        request_cookies = cookies_to_dict(cookies)
        
        response = requests.get(
            url, 
            headers=headers, 
            cookies=request_cookies,
            timeout=10,
            allow_redirects=True
        )
        response.raise_for_status()
        html: str = response.text
        
        if cookies:
            logger.info(f"已携带 {len(cookies)} 个 Cookie 访问 {url}")
            logger.debug(f"重定向后的 URL: {response.url}")
        
        return html
    except requests.exceptions.RequestException as err:
        error_msg: str = f"请求 {url} 失败: {err}"
        logger.error(error_msg)
        raise err

def check_webpage_source(html: str) -> str:
    """
    返回原始网页源代码（不进行解析）
    
    :param html: 网页源代码字符串
    :return: 原始 HTML 字符串；输入无效返回空字符串
    """
    try:
        # 检查输入是否有效
        if not html or not isinstance(html, str):
            error_msg: str = "HTML 内容为空或格式不正确"
            logger.error(error_msg)
            return ""
        
        # 直接返回原始内容，不做任何解析
        logger.info(f"获取网页源代码成功，长度: {len(html)} 字符")
        return html
        
    except Exception as err:
        error_msg: str = f"获取网页源代码失败: {err}"
        logger.error(error_msg)
        return ""