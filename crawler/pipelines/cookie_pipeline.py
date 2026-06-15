import json
import os
import time

def save_cookies_to_json(cookies: list, filepath: str = 'config/cookies.json') -> bool:
    """
    将 Cookie 保存为 JSON 格式文件
    
    :param cookies: Cookie 列表（从 Playwright 获取的格式）
    :param filepath: 保存路径，默认为 config/cookies.json
    :return: 是否保存成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 写入 JSON 文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        
        print(f"Cookie 已保存到: {filepath}")
        return True
    
    except Exception as err:
        print(f"ERROR: 保存 Cookie 失败: {str(err)}")
        return False


def load_cookies_from_json(filepath: str = 'config/cookies.json') -> list | None:
    """
    从 JSON 文件加载 Cookie
    
    :param filepath: Cookie 文件路径
    :return: Cookie 列表，如果文件不存在返回 None
    """
    try:
        if not os.path.exists(filepath):
            print(f"Cookie 文件不存在: {filepath}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        
        print(f"已从 {filepath} 加载 {len(cookies)} 个 Cookie")
        return cookies
    
    except Exception as err:
        print(f"ERROR: 加载 Cookie 失败: {str(err)}")
        return None


def is_cookies_valid(filepath: str = 'config/cookies.json', max_age_days: int = 7) -> bool:
    """
    检查 Cookie 文件是否有效（存在且未过期太久）
    
    :param filepath: Cookie 文件路径
    :param max_age_days: 最大有效期（天）
    :return: 是否有效
    """
    if not os.path.exists(filepath):
        return False
    
    # 检查文件修改时间
    file_mtime = os.path.getmtime(filepath)
    current_time = time.time()
    
    age_days = (current_time - file_mtime) / (24 * 60 * 60)
    
    return age_days <= max_age_days