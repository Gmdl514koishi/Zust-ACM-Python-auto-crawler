from bs4 import BeautifulSoup
from crawler.pipelines.html_pipeline import save_html_to_html
from crawler.utils.request_utils import fetch_webpage, check_webpage_source

def fetch_save_webpage(url: str) -> None:
    """
    爬取并保存网页源代码
    
    :param url: 目标网址
    :return: None
    """

    html: str = fetch_webpage(url)
    webpage_source: str = check_webpage_source(html)
    save_html_to_html(webpage_source, filename=url)
    success_msg: str = f"网页 {url} 源代码爬取完成!"
    print(success_msg)


def find_login_button(html: str) -> dict:
    """
    从 HTML 中查找登录按钮元素。
    
    :param html: 包含登录按钮的 HTML 字符串
    :return: 包含按钮信息的字典，包含 'found'（是否找到）和 'message'（登录状态信息）
    """
    soup = BeautifulSoup(html, 'html.parser')
    login_button = soup.find(
        'button', 
        attrs={
            'data-slot': 'dropdown-menu-trigger',
            'data-sidebar': 'menu-button',
        }
    )

    button_info = {
        'found': False,
        'is_log_in': False,
        'message': '未找到按钮',
    }
    if not login_button:
        return button_info

    button_info['found'] = True
    button_txt = login_button.get_text(strip=True)
    is_logged_out: bool = '未登录' in button_txt or '请先登陆账号' in button_txt
    button_info['is_log_in'] = False if is_logged_out else True
    button_info['message'] = '未登录' if is_logged_out else '已登录'
    return button_info
