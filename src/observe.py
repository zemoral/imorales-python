"""
This module contains logging & tracing operations, primitives, and configuration.


# General

The `Log` class is a wrapper around the standard library's `logging.Logger` class. 
Similarly, the `Log` class should never be instatiated directly & should only be obtained by calling  
`create_global` `create_global_log` `create_log` or obtained indirectly by subclassing the `Trace` class.

The `Trace` class is a wrapper around the `Log` class.
Similarly, the `Trace` class should never be instatiated directly & should only be obtained by calling  
`create_global` `create_global_trace` or `create_trace` functions.

The `GlobalConfig` class defines the configuration used throughout this module.
All configuration members have sensible defaults but aren't applied until `create_global` is called.
The default configuration doesn't interfere with existing handlers defined on the root logger, but it
overrides the root log level. `GlobalConfig.GLOBAL_LOGGER_FORCE_AS_ROOT=True` is an alias for the 
standard library's `dictConfig(force=True)` and removes all existing handlers on the root logger.

---

# TODO
Urgent
- [ ] multiprocessing queue handler
- [ ] tracing event hooks
High
- [ ] format builder w/ common 'tokens' (i.e., ergonomic tracing)
- [ ] global config hotreload
Low
- [ ] `export_global_config_to_file`
- [ ] `update_global_config_with_file`
- [ ] `update_global_config_with_environment`
"""

from __future__ import annotations

from enum import IntEnum, StrEnum
from functools import wraps
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    NOTSET,
    WARN,
    FileHandler,
    Formatter,
    Handler,
    Logger,
    StreamHandler,
    addLevelName,
    captureWarnings,
    getLogger,
)
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler, SysLogHandler
from sys import stderr, stdout
from typing import Callable, Literal, Optional, ParamSpec, Protocol, Self, TypeVar

GLOBAL_TRACE_LEVEL = 25
GLOBAL_TRACE_NAME = "TRACE"
TRACE = GLOBAL_TRACE_LEVEL


BEFORE = 0
AFTER = 1


P = ParamSpec("P")
T = TypeVar("T")


class Level(IntEnum):
    NOTSET = NOTSET
    DEBUG = DEBUG
    INFO = INFO
    TRACE = TRACE
    WARN = WARN
    ERROR = ERROR
    CRITICAL = CRITICAL


class When(IntEnum):
    BEFORE = 0
    AFTER = 1


class Format(StrEnum):
    STANDARD = "{levelname}:{asctime}:{name}:{message}"
    SENSIBLE = "{levelname} : {asctime} : {name} : {message}"
    CUSTOM = "{asctime} :: {levelname} :: {name} :: {message}"
    CUSTOM_TRACING = (
        "{asctime} :: {levelname} :: {name} {processName} {threadName} :: {message}"
    )


class DateFormat(StrEnum):
    CUSTOM = "%a, %d %b %Y at %I:%M%p %Ss %z"
    RFC_2822 = "%a, %d %b %Y %T %z"
    ISO_8601 = "%Y-%m-%dT%H:%M:%S"
    ISO_8601_TZ = "%Y-%m-%dT%H:%M:%S%z"


class LogConfigProtocol(Protocol):
    GLOBAL_LOGGER_NAME: str
    GLOBAL_LOGGER_LEVEL: int
    GLOBAL_LOGGER_STYLE: Literal["{", "$", "%"]
    GLOBAL_LOGGER_FORMAT: str
    GLOBAL_LOGGER_DATEFMT: str
    GLOBAL_LOGGER_PROPOGATE: bool
    GLOBAL_LOGGER_FORCE_AS_ROOT: bool
    GLOBAL_LOGGER_CAPTURE_WARNINGS: bool


class TraceConfigProtocol(Protocol):
    GLOBAL_TRACER_NAME: str
    GLOBAL_TRACER_LEVEL: int
    GLOBAL_TRACER_STYLE: Literal["{", "$", "%"]
    GLOBAL_TRACER_FORMAT: str
    GLOBAL_TRACER_DATEFMT: str
    GLOBAL_TRACER_PROPOGATE: bool


class GlobalConfig(LogConfigProtocol, TraceConfigProtocol):
    # log config protocol members
    GLOBAL_LOGGER_NAME: str = "global"
    GLOBAL_LOGGER_LEVEL: int = DEBUG
    GLOBAL_LOGGER_STYLE: Literal["{", "$", "%"] = "{"
    GLOBAL_LOGGER_FORMAT: str = Format.CUSTOM.value
    GLOBAL_LOGGER_DATEFMT: str = DateFormat.RFC_2822.value
    GLOBAL_LOGGER_PROPOGATE: bool = False
    GLOBAL_LOGGER_FORCE_AS_ROOT: bool = False
    GLOBAL_LOGGER_CAPTURE_WARNINGS: bool = True
    # trace config protocol members
    GLOBAL_TRACER_NAME: str = "events"
    GLOBAL_TRACER_LEVEL: int = TRACE
    GLOBAL_TRACER_STYLE: Literal["{", "$", "%"] = "{"
    GLOBAL_TRACER_FORMAT: str = Format.CUSTOM_TRACING.value
    GLOBAL_TRACER_DATEFMT: str = DateFormat.RFC_2822.value
    GLOBAL_TRACER_PROPOGATE: bool = False


class LogProtocol(Protocol):
    def log(self, level: int, msg: str) -> None:
        ...

    def debug(self, msg: str) -> None:
        self.log(DEBUG, msg)

    def info(self, msg: str) -> None:
        self.log(INFO, msg)

    def warn(self, msg: str) -> None:
        self.log(WARN, msg)

    def warning(self, msg: str) -> None:
        self.log(WARN, msg)

    def error(self, msg: str) -> None:
        self.log(ERROR, msg)

    def exception(self, msg: str) -> None:
        self.log(ERROR, msg)

    def critical(self, msg: str) -> None:
        self.log(CRITICAL, msg)

    def fatal(self, msg: str) -> None:
        self.log(CRITICAL, msg)


class TraceProtocol(LogProtocol, Protocol):
    def span(self, name: str) -> Self:
        ...

    def trace(self, msg: str) -> None:
        self.log(TRACE, msg)


class Log(LogProtocol):
    __slots__ = "name", "level", "logger"

    def __init__(self, name: str, level: int, logger: Optional[Logger] = None) -> None:
        self.name = name
        self.level = Level(level)
        self.logger = logger if logger else getLogger(name)
        self.logger.setLevel(self.level)
        return

    def __repr__(self) -> str:
        return f"Log(name={self.name}, level={self.level.name})"

    def log(self, level: int, msg: str) -> None:
        return self.logger.log(level, msg)


class Trace(TraceProtocol):
    __slots__ = ("_log",)

    def __init__(self, name: str, level: int, logger: Optional[Logger] = None) -> None:
        self._log = Log(name, level, logger=logger)

    def __repr__(self) -> str:
        return f"Trace(name={self._log.name}, level={self._log.level.name})"

    def log(self, level: int, msg: str) -> None:
        return self._log.log(level, msg)

    def span(self, name: str) -> Trace:
        return Trace(f"{self._log.name}.{name}", self._log.level.value)


def update_global_config(
    config: object | LogConfigProtocol | TraceConfigProtocol | type[GlobalConfig],
) -> None:
    def global_config_attr(name: str) -> bool:
        return name.startswith("GLOBAL") and hasattr(GlobalConfig, name)

    for attr in filter(global_config_attr, vars(config).keys()):
        setattr(GlobalConfig, attr, getattr(config, attr))
    return


def create_global_log(handlers: list[Handler]) -> Log:
    # apply minimal configuration to the root logger
    root_logger = getLogger()
    root_logger.setLevel(GlobalConfig.GLOBAL_LOGGER_LEVEL)
    captureWarnings(GlobalConfig.GLOBAL_LOGGER_CAPTURE_WARNINGS)
    # create a pseudo global logger to prevent interfering with other libraries
    global_logger = getLogger(GlobalConfig.GLOBAL_LOGGER_NAME)
    global_logger.setLevel(GlobalConfig.GLOBAL_LOGGER_LEVEL)
    global_logger.propagate = GlobalConfig.GLOBAL_LOGGER_PROPOGATE
    # format & add handlers
    for handler in handlers:
        handler.setFormatter(
            Formatter(
                fmt=GlobalConfig.GLOBAL_LOGGER_FORMAT,
                style=GlobalConfig.GLOBAL_LOGGER_STYLE,
                datefmt=GlobalConfig.GLOBAL_LOGGER_DATEFMT,
            )
        )
        global_logger.addHandler(handler)
    # override existing root handlers if enabled
    if GlobalConfig.GLOBAL_LOGGER_FORCE_AS_ROOT:
        dictConfig(
            {
                "version": 1,
                "force": True,
                "fmt": GlobalConfig.GLOBAL_LOGGER_FORMAT,
                "level": GlobalConfig.GLOBAL_LOGGER_LEVEL,
                "datefmt": GlobalConfig.GLOBAL_LOGGER_DATEFMT,
                "handlers": handlers,
            }
        )
    return Log(
        name=GlobalConfig.GLOBAL_LOGGER_NAME,
        level=GlobalConfig.GLOBAL_LOGGER_LEVEL,
        logger=global_logger,
    )


def create_global_trace(handlers: list[Handler]) -> Trace:
    # add custom level for tracing
    addLevelName(GLOBAL_TRACE_LEVEL, GLOBAL_TRACE_NAME)
    # create trace specific logger
    name = f"{GlobalConfig.GLOBAL_LOGGER_NAME}.{GlobalConfig.GLOBAL_TRACER_NAME}"
    trace_logger = getLogger(name)
    trace_logger.setLevel(GlobalConfig.GLOBAL_TRACER_LEVEL)
    trace_logger.propagate = GlobalConfig.GLOBAL_TRACER_PROPOGATE
    # format & add handlers
    for handler in handlers:
        handler.setFormatter(
            Formatter(
                fmt=GlobalConfig.GLOBAL_TRACER_FORMAT,
                style=GlobalConfig.GLOBAL_TRACER_STYLE,
                datefmt=GlobalConfig.GLOBAL_TRACER_DATEFMT,
            )
        )
        trace_logger.addHandler(handler)
    return Trace(
        name=name,
        level=GlobalConfig.GLOBAL_TRACER_LEVEL,
        logger=trace_logger,
    )


def create_global(
    log: Optional[list[Handler]] = None,
    trace: Optional[list[Handler]] = None,
    config: Optional[
        object | LogConfigProtocol | TraceProtocol | type[GlobalConfig]
    ] = None,
) -> tuple[Log, Trace]:
    if config:
        update_global_config(config)
    if log is None:
        log = [
            create_handler_stdout(level=GlobalConfig.GLOBAL_LOGGER_LEVEL),
            create_handler_stderr(level=ERROR),
        ]
    if trace is None:
        trace = [
            create_handler_stdout(level=GlobalConfig.GLOBAL_TRACER_LEVEL),
        ]
    return (create_global_log(log), create_global_trace(trace))


def create_log(
    namespace: str,
    level: int = GlobalConfig.GLOBAL_LOGGER_LEVEL,
) -> Log:
    name = f"{GlobalConfig.GLOBAL_LOGGER_NAME}.{namespace}"
    return Log(name, level)


def create_trace(
    namespace: str,
    level: int = GlobalConfig.GLOBAL_TRACER_LEVEL,
) -> Trace:
    name = f"{GlobalConfig.GLOBAL_LOGGER_NAME}.{GlobalConfig.GLOBAL_TRACER_NAME}.{namespace}"
    return Trace(name, level)


def create_handler_stdout(
    level: int | Level = GlobalConfig.GLOBAL_LOGGER_LEVEL,
) -> StreamHandler:
    handler = StreamHandler(stream=stdout)
    handler.setLevel(level)
    return handler


def create_handler_stderr(level: int | Level = Level.ERROR) -> StreamHandler:
    handler = StreamHandler(stream=stderr)
    handler.setLevel(level)
    return handler


def create_handler_syslog(
    host: str = "localhost",
    port: int = 514,
    level: int | Level = GlobalConfig.GLOBAL_LOGGER_LEVEL,
) -> SysLogHandler:
    handler = SysLogHandler(address=(host, port))
    handler.setLevel(level)
    return handler


def create_handler_file(
    path: str,
    mode: str = "a",
    encoding: str | None = None,
    level: int | Level = GlobalConfig.GLOBAL_LOGGER_LEVEL,
) -> FileHandler:
    handler = FileHandler(path, mode=mode, encoding=encoding)
    handler.setLevel(level)
    return handler


def create_handler_file_rotating(
    path: str,
    mode: str = "a",
    max_files: int = 10,
    max_bytes: int = 1_000_000,
    encoding: str | None = None,
    level: int | Level = GlobalConfig.GLOBAL_LOGGER_LEVEL,
) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        path,
        mode=mode,
        backupCount=max_files,
        maxBytes=max_bytes,
        encoding=encoding,
    )
    handler.setLevel(level)
    return handler


def logged(
    log: Log, msg: str, when: int = BEFORE, level: int = INFO
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def before(func: Callable[P, T]):
        @wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            log.log(level, msg)
            return func(*args, **kwargs)

        return wrapped

    def after(func: Callable[P, T]):
        @wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            value = func(*args, **kwargs)
            log.log(log.level, msg)
            return value

        return wrapped

    if when == BEFORE:
        return before
    if when == AFTER:
        return after
    raise ValueError(f"{when=} during {log.name} {msg}")


def traced(
    trace: Trace, msg: str, when: int = BEFORE, level: int = TRACE
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def before(func: Callable[P, T]):
        @wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            trace.log(level, msg)
            return func(*args, **kwargs)

        return wrapped

    def after(func: Callable[P, T]):
        @wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            value = func(*args, **kwargs)
            trace.log(level, msg)
            return value

        return wrapped

    if when == BEFORE:
        return before
    if when == AFTER:
        return after
    raise ValueError(f"{when=} during {trace._log.name} {msg}")
