import requests

headers: dict[str, str] = {
    "User-Agent": "ZUST-ACM-Crawler/1.0 (+https://github.com/Gmdl514koishi/Zust-ACM-Python-auto-crawler)",
    "From": "1251004020"
}

def fetch_webpage(url: str) -> str:
    """
    获取网页源代码

    :param url: 目标网址
    :return: 网页源代码
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html: str = response.text
        return html
    except requests.exceptions.RequestException as err:
        error_msg: str = f"请求 {url} 失败: {err}"
        print(error_msg)
        raise err

def check_webpage_source(html: str) -> str:
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