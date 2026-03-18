# services/utils/logger.py

import logging
import uuid

import colorlog

TRACE_ID = None

def new_trace():
    global TRACE_ID
    TRACE_ID = str(uuid.uuid4())[:4]
    return TRACE_ID

def get_trace():
    return TRACE_ID

def get_logger(name: str):
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(asctime)s.%(msecs)03d %(log_color)s[%(name)s][%(trace)s]%(reset)s %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    handler.setFormatter(formatter)
    logger = colorlog.getLogger(name)
    if not logger.handlers:
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

class TraceAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return msg, {"extra": {"trace": get_trace()}}