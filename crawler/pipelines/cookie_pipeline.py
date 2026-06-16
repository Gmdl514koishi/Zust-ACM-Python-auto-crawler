import json
import logging
import os
import time
from typing import Optional, List, Dict, Any

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def save_cookies_to_json(cookies: List[Dict[str, Any]], filepath: str = 'config/cookies.json', merge: bool = True) -> bool:
    """
    将 Cookie 保存为 JSON 格式文件
    
    :param cookies: Cookie 列表（从 Playwright 获取的格式）
    :param filepath: 保存路径，默认为 config/cookies.json
    :param merge: 是否合并更新(True: 合并现有 Cookie, False: 覆盖)
    :return: 是否保存成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if merge and os.path.exists(filepath):
            # 检查新 Cookie 是否为空
            if not cookies or len(cookies) == 0:
                logger.info("新 Cookie 为空，跳过更新")
                return True
            
            # 加载现有的 Cookie
            existing_cookies = load_cookies_from_json(filepath)
            if existing_cookies:
                # 构建现有 Cookie 的字典（按 name 分组）
                existing_cookies_dict = {}
                for cookie in existing_cookies:
                    cookie_name = cookie.get('name')
                    if cookie_name:
                        existing_cookies_dict[cookie_name] = cookie
                
                # 合并新 Cookie（新的会覆盖旧的同名 Cookie）
                for new_cookie in cookies:
                    cookie_name = new_cookie.get('name')
                    if cookie_name:
                        existing_cookies_dict[cookie_name] = new_cookie
                
                # 转换回列表
                cookies = list(existing_cookies_dict.values())
                logger.info(f"已合并 {len(cookies)} 个 Cookie")
        
        # 写入 JSON 文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Cookie 已保存到: {filepath}")
        return True
    
    except Exception as err:
        logger.error(f"保存 Cookie 失败: {str(err)}")
        return False


def load_cookies_from_json(filepath: str = 'config/cookies.json') -> Optional[List[Dict[str, Any]]]:
    """
    从 JSON 文件加载 Cookie
    
    :param filepath: Cookie 文件路径
    :return: Cookie 列表，如果文件不存在或加载失败返回 None
    """
    try:
        if not os.path.exists(filepath):
            logger.error(f"Cookie 文件不存在: {filepath}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        
        if not isinstance(cookies, list):
            logger.error("Cookie 文件格式错误，期望是列表")
            return None
        
        logger.info(f"已从 {filepath} 加载 {len(cookies)} 个 Cookie")
        return cookies
    
    except json.JSONDecodeError as err:
        logger.error(f"Cookie 文件解析失败: {str(err)}")
        return None
    except Exception as err:
        logger.error(f"加载 Cookie 失败: {str(err)}")
        return None


def is_cookie_expired(cookie: Dict[str, Any]) -> bool:
    """
    检查单个 Cookie 是否过期
    
    :param cookie: 单个 Cookie 字典
    :return: 是否过期
    """
    expires = cookie.get('expires')
    
    # 如果没有 expires 字段，视为会话 Cookie（不过期）
    if expires is None or expires == -1:
        return False
    
    # expires 可能是整数（秒）或字符串
    try:
        expires_time = float(expires)
        current_time = time.time()
        return current_time > expires_time
    except (ValueError, TypeError):
        logger.warning(f"无法解析 Cookie 过期时间: {expires}")
        return False


def is_cookies_valid(filepath: str = 'config/cookies.json', max_age_days: int = 7) -> bool:
    """
    检查 Cookie 文件是否有效（存在、未过期且不过期太久）
    
    :param filepath: Cookie 文件路径
    :param max_age_days: 最大文件有效期（天），仅在没有 expires 字段时使用
    :return: 是否有效
    """
    # 检查文件是否存在
    if not os.path.exists(filepath):
        logger.debug(f"Cookie 文件不存在: {filepath}")
        return False
    
    # 检查文件修改时间（作为备用检查）
    file_mtime = os.path.getmtime(filepath)
    current_time = time.time()
    age_days = (current_time - file_mtime) / (24 * 60 * 60)
    
    if age_days > max_age_days:
        logger.warning(f"Cookie 文件已超过 {max_age_days} 天未更新")
    
    # 加载并检查每个 Cookie 的过期时间
    cookies = load_cookies_from_json(filepath)
    if not cookies:
        return False
    
    expired_count = 0
    for cookie in cookies:
        if is_cookie_expired(cookie):
            expired_count += 1
            logger.debug(f"Cookie [{cookie.get('name')}] 已过期")
    
    if expired_count > 0:
        logger.warning(f"发现 {expired_count} 个过期 Cookie，总共有 {len(cookies)} 个")
    
    # 如果所有 Cookie 都过期，返回 False
    return expired_count < len(cookies)


def clean_expired_cookies(filepath: str = 'config/cookies.json') -> bool:
    """
    清理过期的 Cookie 并保存到文件
    
    :param filepath: Cookie 文件路径
    :return: 是否清理成功
    """
    cookies = load_cookies_from_json(filepath)
    if not cookies:
        return False
    
    original_count = len(cookies)
    valid_cookies = [cookie for cookie in cookies if not is_cookie_expired(cookie)]
    removed_count = original_count - len(valid_cookies)
    
    if removed_count > 0:
        logger.info(f"清理 {removed_count} 个过期 Cookie")
        return save_cookies_to_json(valid_cookies, filepath, merge=False)
    
    logger.info("没有过期 Cookie 需要清理")
    return True


def validate_cookies(cookies: List[Dict[str, Any]]) -> bool:
    """
    验证 Cookie 列表的格式是否正确
    
    :param cookies: Cookie 列表
    :return: 是否有效
    """
    if not isinstance(cookies, list):
        logger.error("Cookie 数据必须是列表")
        return False
    
    required_fields = ['name', 'value']
    
    for i, cookie in enumerate(cookies):
        if not isinstance(cookie, dict):
            logger.error(f"第 {i} 个 Cookie 不是字典格式")
            return False
        
        for field in required_fields:
            if field not in cookie:
                logger.error(f"第 {i} 个 Cookie 缺少必要字段: {field}")
                return False
        
        # 验证 expires 字段类型
        if 'expires' in cookie and cookie['expires'] is not None:
            try:
                float(cookie['expires'])
            except (ValueError, TypeError):
                logger.error(f"第 {i} 个 Cookie 的 expires 字段格式不正确")
                return False
    
    logger.debug(f"验证通过，共 {len(cookies)} 个 Cookie")
    return True