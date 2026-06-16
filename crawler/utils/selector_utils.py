import json
import os
from venv import logger
from crawler.utils.logging_utils import setup_logging

# 配置日志
logger = setup_logging()

def load_selectors(form_type: str, filepath: str = 'config/selectors.json') -> dict:
    """
    从 JSON 文件加载选择器配置
    
    :param form_type: 表单类型
    :param filepath: 配置文件路径
    :return: 选择器字典
    """
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"选择器配置文件不存在: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            selectors = json.load(f)
        
        if form_type not in selectors:
            raise ValueError(f"表单类型 {form_type} 不存在于选择器配置中")
        
        selectors = selectors[form_type]
        
        logger.info(f"已加载 {len(selectors)} 个选择器配置，表单类型: {form_type}")
        return selectors
    
    except Exception as err:
        logger.error(f"ERROR: 加载选择器配置失败: {str(err)}")
        return {}