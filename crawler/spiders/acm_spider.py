def fetch_webpage_source(html: str) -> str:
    """
    返回原始网页源代码（不进行解析）
    
    :param html: 网页源代码字符串
    :return: 原始 HTML 字符串；输入无效返回空字符串
    """
    try:
        # 检查输入是否有效
        if not html or not isinstance(html, str):
            print("错误: HTML 内容为空或格式不正确")
            return ""
        
        # 直接返回原始内容，不做任何解析
        print(f"获取网页源代码成功，长度: {len(html)} 字符")
        return html
        
    except Exception as err:
        # 内部处理所有异常
        print(f"获取网页源代码失败: {str(err)}")
        return ""