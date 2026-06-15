import logging
import os
from datetime import datetime


def setup_logging(log_dir: str = 'logs', log_name: str = 'crawler') -> logging.Logger:
    """
    配置日志输出到指定文件夹，同时输出到控制台
    
    :param log_dir: 日志目录
    :param log_name: 日志文件名前缀
    :return: 配置好的 logger 对象
    """
    os.makedirs(log_dir, exist_ok=True)
    
    # 生成带时间戳的日志文件名
    log_filename = os.path.join(log_dir, f'{log_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # 避免重复添加 handler
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_logger.setLevel(logging.INFO)
        
        # 文件 handler
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台 handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)
