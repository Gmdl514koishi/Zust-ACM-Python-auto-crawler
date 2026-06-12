import os
import requests
from requests_html import HTMLSession

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

# def save_full_webpage(url: str, filename: str = "full_page.html") -> None:
#     """
#     使用 requests-html 获取完整渲染后的网页（包含 JavaScript 执行结果）
    
#     :param url: 目标网址
#     :param filename: 保存的文件名，默认 full_page.html
#     """
#     try:
#         # 1. 创建会话
#         session = HTMLSession()
#         print(f"正在获取并渲染网页: {url}")
        
#         # 2. 发送请求
#         response = session.get(url, timeout=15)
#         response.raise_for_status()  # 检查 HTTP 状态码
        
#         # 3. 渲染 JavaScript（增加超时时间）
#         print("正在渲染 JavaScript...")
#         response.html.render(timeout=30, sleep=3)
        
#         # 4. 获取渲染后的 HTML
#         html_content = response.html.html
        
#         # 5. 保存到文件
#         os.makedirs("./data", exist_ok=True)
#         filepath = os.path.join("./data", filename)
        
#         with open(filepath, "w", encoding="utf-8") as f:
#             f.write(html_content)
        
#         print(f"完整网页已保存到: {filepath}")
#         print(f"文件大小: {len(html_content)} 字符")
        
#     except requests.exceptions.RequestException as err:
#         print(f"网络请求失败 [{url}]: {str(err)}")
#     except Exception as err:
#         print(f"保存完整网页失败 [{url}]: {str(err)}")
#         # 确保会话总是关闭
#         if session:
#             try:
#                 session.close()
#             except:
#                 pass