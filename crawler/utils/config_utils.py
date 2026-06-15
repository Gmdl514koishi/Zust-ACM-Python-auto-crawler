from dotenv import load_dotenv
import os

load_dotenv('config/.env')

def get_email_from_env() -> str:
    """
    从 .env 中读取用户邮箱配置

    :return: 用户邮箱
    """
    email = os.getenv('ACM_EMAIL')
    if not email:
        raise EOFError("未配置邮箱") # 后续添加写入邮箱函数
    return email