import os
from loguru import logger as loguru_logger
from pathlib import Path

CONFIG_MODULE_DIR = Path(__file__).parent.resolve()
os.environ["LOGURU_LEVEL"] = "INFO"

FILE_HANDLER_ADDED = False

def get_logger(module_name:str):
    app_log = os.path.join(os.path.dirname(CONFIG_MODULE_DIR), "logs", "app.log")
    loguru_logger.add(app_log, rotation="500 MB", retention="10 days",# level="INFO",
               format="{time} | {level} | " + module_name + ":{function}:{line} - {message}")
    return loguru_logger


