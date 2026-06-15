from playwright.sync_api import Page, ElementHandle

def find_element(page: Page, selector: str, timeout: int = 5000) -> ElementHandle | None:
    """
    查找页面元素

    :param page: Playwright page 对象
    :param selector: CSS 选择器
    :param timeout: 等待超时时间（毫秒）
    :return: 元素对象或 None
    """
    return page.wait_for_selector(selector, timeout=timeout)


def click_element(page: Page, selector: str, timeout: int = 5000) -> bool:
    """
    点击页面元素

    :param page: Playwright page 对象
    :param selector: CSS 选择器
    :param timeout: 等待超时时间（毫秒）
    :return: 是否成功
    """
    element = find_element(page, selector, timeout)
    if element:
        element.click()
        return True
    return False


def fill_element(page: Page, selector: str, value: str, timeout: int = 5000) -> bool:
    """
    填充页面元素

    :param page: Playwright page 对象
    :param selector: CSS 选择器
    :param value: 要填入的值
    :param timeout: 等待超时时间（毫秒）
    :return: 是否成功
    """
    element = find_element(page, selector, timeout)
    if element:
        element.fill(value)
        return True
    return False