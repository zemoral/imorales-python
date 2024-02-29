"""
This module contains & generates commands

A command is one callback and unique name
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from functools import wraps
from types import GenericAlias
from typing import Callable, Concatenate, Generic

from src.hint import TT, Callback, Decorator, Generic, Optional, P, Protocol, T, Unpack


class Runtime(IntEnum):
    SYNC = 0
    ASYNC = 1
    THREADED = 2
    MULTIPROCESS = 3


class Schedule(IntEnum):
    ...


class Sync(Schedule):
    BEFORE = 0
    FAILURE = 1
    SUCCESS = 2
    ALWAYS = 3
    LOOP = 4


class CommandProtocol(Protocol[T, Unpack[TT]]):
    name: str
    command: Callable[[Unpack[TT], T], None]


class InputProtocol(Protocol[T, Unpack[TT]]):
    args: tuple[Unpack[TT]]
    kwargs: T


class HookProtocol(Protocol):
    hook: Callback
    when: int | Schedule
    runtime: int | Runtime


class SubscribeProtocol(
    CommandProtocol[T, Unpack[TT]],
    HookProtocol,
    Protocol,
):
    ...


class ExecuteProtocol(
    CommandProtocol[T, Unpack[TT]],
    InputProtocol[T, Unpack[TT]],
    Protocol,
):
    ...


class ScheduleProtocol(
    CommandProtocol[T, Unpack[TT]],
    InputProtocol[T, Unpack[TT]],
    HookProtocol,
    Protocol,
):
    ...
