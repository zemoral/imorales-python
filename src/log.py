"""
This module contains common logging operations & utilities
"""

from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    NOTSET,
    WARN,
    Formatter,
    Logger,
    getLogger,
)

GLOBAL_FORMAT = Formatter(
    fmt="%()s :: %()s :: %()s :: %()s :: %()s :: %()s :: %()s",
)
GLOBAL_LOGGER = getLogger(
    "GLOBAL"
)


class Trace(Logger):
    def __init__(self, name: str, level: int = NOTSET) -> None:
        pass
