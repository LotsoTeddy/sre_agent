from datetime import datetime, timedelta

def get_current_time() -> str:
    """获取当前时间的字符串表示（格式：YYYY-MM-DD HH:MM:SS）"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_yesterday_time() -> str:
    """用来模拟几天之内工作过了的，把时间提早到昨天"""
    # 获取当前时间
    now = datetime.now()
    # 将时间往前调整一天
    yesterday = now - timedelta(days=1)
    # 以指定格式返回昨天的时间字符串
    return yesterday.strftime("%Y-%m-%d %H:%M:%S")