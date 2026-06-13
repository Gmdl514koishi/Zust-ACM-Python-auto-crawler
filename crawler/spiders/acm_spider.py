from bs4 import BeautifulSoup

def fetch_save_webpage(url: str) -> None:
    """
    爬取并保存网页源代码
    
    :param url: 目标网址
    :return: None
    """
    from crawler.pipelines.html_pipeline import save_html_to_html
    from crawler.spiders.acm_spider import fetch_webpage_source
    from crawler.utils.request_utils import fetch_webpage

    html: str = fetch_webpage(url)
    webpage_source: str = fetch_webpage_source(html)
    save_html_to_html(webpage_source, filename=url)
    success_msg: str = f"网页 {url} 源代码爬取完成!"
    print(success_msg)

def fetch_webpage_source(html: str) -> str:
    """
    返回原始网页源代码（不进行解析）
    
    :param html: 网页源代码字符串
    :return: 原始 HTML 字符串；输入无效返回空字符串
    """
    try:
        # 检查输入是否有效
        if not html or not isinstance(html, str):
            error_msg: str = "错误: HTML 内容为空或格式不正确"
            print(error_msg)
            return ""
        
        # 直接返回原始内容，不做任何解析
        # 成功获取内容，返回原始 HTML
        success_msg: str = f"获取网页源代码成功，长度: {len(html)} 字符"
        print(success_msg)
        return html
        
    except Exception as err:
        # 内部处理所有异常
        error_msg: str = f"获取网页源代码失败: {err}"
        print(error_msg)
        return ""

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
        'message': '未找到按钮',
    }
    if not login_button:
        return button_info

    button_info['found'] = True
    button_txt = login_button.get_text(strip=True)
    is_logged_out: bool = '未登录' in button_txt or '请先登陆账号' in button_txt
    button_info['message'] = '未登录' if is_logged_out else '已登录'
    return button_info
