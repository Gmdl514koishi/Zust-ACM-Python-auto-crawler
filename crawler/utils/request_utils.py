import requests

def fetch_page(url: str) -> str:
    """
    获取网页源代码

    :param url: 目标网址
    :return: 网页源代码
    """
    headers = {
        "User-Agent": "ZUST-ACM-Crawler/1.0 (+https://github.com/Gmdl514koishi/Zust-ACM-Python-auto-crawler)",
        "From": "1251004020"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
        return html
    except requests.exceptions.RequestException as err:
        print(f"请求失败: {err}")
        raise err
