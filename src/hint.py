from typing import (
    Callable,
    Concatenate,
    Generic,
    Optional,
    ParamSpec,
    Protocol,
    TypeAlias,
    TypeVar,
    TypeVarTuple,
    Unpack,
)

_ = Optional
_ = Generic
_ = Protocol
_ = Concatenate
_ = Unpack

T = TypeVar("T")
T2 = TypeVar("T2")
P = ParamSpec("P")
P2 = ParamSpec("P2")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
TT = TypeVarTuple("TT")
TT2 = TypeVarTuple("TT2")

Fn: TypeAlias = Callable
Callback: TypeAlias = Callable[[], None]
Constructor: TypeAlias = Callable[[], T]
Decorator: TypeAlias = Callable[[Callable[P, T]], Callable[P, T]]
DecoratorFactory: TypeAlias = Callable[P2, Decorator[P, T]]
