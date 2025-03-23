import logging

from pythonjsonlogger import json

json_formatter = json.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(filename)s"
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(json_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler],
)


def get_logger(name):
    return logging.getLogger(name)
