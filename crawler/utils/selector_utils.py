import json
import os

def load_selectors(filepath: str = 'config/selectors.json') -> dict:
    """
    从 JSON 文件加载选择器配置
    
    :param filepath: 配置文件路径
    :return: 选择器字典
    """
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"选择器配置文件不存在: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            selectors = json.load(f)
        
        print(f"已加载 {len(selectors)} 个选择器配置")
        return selectors
    
    except Exception as err:
        print(f"ERROR: 加载选择器配置失败: {str(err)}")
        return {}