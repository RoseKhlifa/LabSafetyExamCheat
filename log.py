from datetime import datetime
import time

def get_current_time():
    # 获取当前 datetime 对象
    current_datetime = datetime.now()
    # 按照 时:分:秒 的格式格式化
    formatted_time = current_datetime.strftime("%H:%M:%S")
    return formatted_time


def log(msg, cost=None):
    """
    统一日志输出
    :param msg: 日志内容
    :param cost: 上一步耗时（秒），可选
    """
    time_str = get_current_time()
    if cost is not None:
        print(f"[{time_str}][+] {msg}，耗时 {cost:.3f}s")
    else:
        print(f"[{time_str}][+] {msg}")
