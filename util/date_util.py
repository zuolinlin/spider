import time


def get_date(millisecond):
    """
    时间转换
    :param millisecond: 毫秒
    :return:
    """
    if millisecond is None or millisecond < 0:
        return None
    return time.localtime(millisecond/1000)