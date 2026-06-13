def main():
    url: dict[str, str] = {
        "root": "https://acm.zust.edu.cn",
    }

    from .crawler.spiders.acm_spider import fetch_save_webpage
    fetch_save_webpage(url["root"])

if __name__ == "__main__":
    main()