from datetime import datetime
import pytz


def get_now():
    # 获取当前时间
    now = datetime.now()
    # 设置时区为中国标准时间
    tz = pytz.timezone('Asia/Shanghai')
    # 将当前时间转换为中国标准时间
    now = now.astimezone(tz)
    return now
