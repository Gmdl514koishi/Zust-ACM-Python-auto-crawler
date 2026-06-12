from crawler.utils.request_utils import fetch_webpage
from crawler.spiders.acm_spider import fetch_webpage_source
from crawler.pipelines.html_pipeline import save_html_to_html

def main():
    target_url = "https://acm.zust.edu.cn/rank"

    html = fetch_webpage(target_url)
    webpage_source = fetch_webpage_source(html)
    save_html_to_html(webpage_source)
    print("网页源代码爬取完成！")

if __name__ == "__main__":
    main()