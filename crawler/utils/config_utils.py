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

def get_student_id_from_env() -> str:
    """
    从 .env 中读取学生学号配置

    :return: 学生学号
    """
    student_id = os.getenv('STUDENT_ID')
    if not student_id:
        raise EOFError("未配置学生学号") # 后续添加写入学生学号函数
    return student_id

def get_student_password_from_env() -> str:
    """
    从 .env 中读取学生密码配置

    :return: 学生密码
    """
    student_password = os.getenv('STUDENT_PASSWORD')
    if not student_password:
        raise EOFError("未配置学生密码") # 后续添加写入学生密码函数
    return student_password

def get_webvpn_password_from_env() -> str:
    """
    从 .env 中读取 WebVPN 密码配置

    :return: WebVPN 密码
    """
    webvpn_password = os.getenv('WEBVPN_PASSWORD')
    if not webvpn_password:
        raise EOFError("未配置 WebVPN 密码") # 后续添加写入 WebVPN 密码函数
    return webvpn_password

def get_webvpn_username_from_env() -> str:
    """
    从 .env 中读取 WebVPN 用户名配置

    :return: WebVPN 用户名
    """
    webvpn_username = os.getenv('WEBVPN_USERNAME')
    if not webvpn_username:
        raise EOFError("未配置 WebVPN 用户名") # 后续添加写入 WebVPN 用户名函数
    return webvpn_username
