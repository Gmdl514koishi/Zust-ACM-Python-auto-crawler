def html_to_str(filepath: str) -> str:
    """
    读取 HTML 文件并返回字符串

    :param filepath: 文件路径
    :return: html文件转换后的字符串 
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()