from datetime import datetime

def get_current_time() -> str:
    """获取当前时间的字符串表示（格式：YYYY-MM-DD HH:MM:SS）"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")