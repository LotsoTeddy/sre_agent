import os
from loguru import logger as loguru_logger
from pathlib import Path

CONFIG_MODULE_DIR = Path(__file__).parent.resolve()
# os.environ["LOGURU_LEVEL"] = "INFO"

FILE_HANDLER_ADDED = False

# 移除默认处理程序
# loguru_logger.remove()

app_log = os.path.join(os.path.dirname(CONFIG_MODULE_DIR), "logs", "app.log")
# 在日志格式中添加文件、函数和行号信息
loguru_logger.add(
    app_log,
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    format="{time} | {level} | {file}:{function}:{line} - {message}"
)

def get_logger(module_name: str):
    return loguru_logger.bind(module=module_name)