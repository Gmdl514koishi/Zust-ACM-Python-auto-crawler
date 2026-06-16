from crawler.spiders.acm_spider import login
from crawler.spiders.acm_spider import fetch_save_webpage, find_login_button
from crawler.utils.file_utils import html_to_str

def main():
    url: dict[str, str] = {
        'webvpn_username': 'https://webvpn.zust.edu.cn',
        'root': 'https://acm.zust.edu.cn',
    }

    try:
        fetch_save_webpage(url['root'])

        # 检查登录状态
        button_info =  find_login_button(html_to_str('data/acm.zust.edu.cn.html'))
        if button_info['found'] == False:
            print("未找到登录按钮")
            return
        print(f"登录状态: {button_info['message']}")

        if button_info['is_log_in'] == False:
            login(url)
    except Exception as err:
        print(f"程序出错，终止执行: {err}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()