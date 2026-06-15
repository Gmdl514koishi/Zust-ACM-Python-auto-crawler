from crawler.utils.config_utils import get_email_from_env
from crawler.utils.intellijudge_utils import click_element, fill_element
from crawler.utils.logging_utils import setup_logging
from crawler.utils.selector_utils import load_selectors
from playwright.sync_api import Page

# 配置日志
logger = setup_logging()

# 选择器常量
SELECTORS = load_selectors()

def fill_email(page: Page) -> bool:
    """
    在登录页面自动填入邮箱
    
    :param page: Playwright page 对象
    :return: 是否成功填写邮箱
    """
    user_email = get_email_from_env()
    if not user_email:
        logger.error("未获取到邮箱配置")
        return False

    # 使用 fill_element 函数填入邮箱
    if not fill_element(page, SELECTORS['email_input'], user_email, timeout=5000):
        logger.error("未找到邮箱输入框")
        return False
    
    # 点击 Continue 按钮
    if not click_element(page, SELECTORS['continue_button'], timeout=5000):
        logger.error("未找到 Continue 按钮")
        return False
    
    logger.info(f"已填写邮箱: {user_email}")
    return True


def fill_verification_code(page: Page) -> bool:
    """
    从终端输入验证码并提交
    
    :param page: Playwright page 对象
    :return: 是否成功填写验证码
    """
    # 从终端获取验证码
    code = input("请输入验证码(6位数字): ").strip()
    
    if not code:
        logger.error("验证码不能为空")
        return False
    
    # 检查验证码是否为6位数字
    if not code.isdigit() or len(code) != 6:
        logger.error("验证码必须为6位数字")
        return False
    
    # 填入验证码
    if not fill_element(page, SELECTORS['verification_code_input'], code, timeout=5000):
        logger.error("未找到验证码输入框")
        return False
    
    # 点击 Continue 按钮
    if not click_element(page, SELECTORS['continue_button'], timeout=5000):
        logger.error("未找到 Continue 按钮")
        return False
    
    logger.info(f"已提交验证码")
    return True
