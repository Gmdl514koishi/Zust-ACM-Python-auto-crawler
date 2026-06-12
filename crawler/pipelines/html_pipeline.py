import os
import requests

def save_html_to_html(html_content: str, filename: str = "webpage.html") -> None:
    """
    将原始 HTML 字符串保存到 data/ 文件夹中
    
    :param html_content: 原始 HTML 字符串
    :param filename: 保存的文件名，默认 webpage.html
    """
    try:
        if not html_content or not isinstance(html_content, str):
            print("错误: HTML 内容为空或格式不正确")
            return
        data_dir = "./data"
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"HTML 内容已成功保存到: {file_path}")
        
    except Exception as err:
        print(f"保存 HTML 文件失败 [{filename}]: {str(err)}")

    