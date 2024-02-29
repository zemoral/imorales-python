"""
This module contains utilities for analyzing, generating & transforming host environments
"""

from os import getenv

from src.hint import Optional, T


def environment_variable_into(t: type[T], variable: str) -> T:
    value = getenv(variable, None)
    if variable is None:
        raise ValueError(f"Missing environment variable {variable}")
    return t(value)


def environment_variable_into_optional(t: type[T], variable: str) -> Optional[T]:
    value = getenv(variable, None)
    if variable is None:
        return variable
    return t(value)
