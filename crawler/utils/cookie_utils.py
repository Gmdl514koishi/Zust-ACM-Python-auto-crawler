from typing import List, Dict, Any


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