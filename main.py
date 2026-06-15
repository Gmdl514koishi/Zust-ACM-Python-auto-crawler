from crawler.spiders.acm_spider import login
from crawler.spiders.acm_spider import fetch_save_webpage, find_login_button
from crawler.utils.file_utils import html_to_str

def main():
    url: dict[str, str] = {
        'root': 'https://acm.zust.edu.cn',
    }

    fetch_save_webpage(url['root'])

    button_info =  find_login_button(html_to_str('data/acm.zust.edu.cn.html'))
    if button_info['found'] == False:
        print("未找到登录按钮")
        return
    print(f"登录状态: {button_info['message']}")

    if button_info['is_log_in'] == False:
        login(url['root'])

if __name__ == "__main__":
    main()