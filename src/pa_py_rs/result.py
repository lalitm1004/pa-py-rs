from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, Optional, cast

from pa_py_rs.panic import panic

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")
F = TypeVar("F")


class Result(Generic[T, E]):
    def __init__(self):
        raise NotImplementedError("Use Ok() of Err() to create Result instance")

    def is_ok(self) -> bool:
        """Returns True if the result is Ok"""
        return isinstance(self, Ok)

    def is_ok_and(self, value: T) -> bool:
        """Returns True if the result is Ok and the provided value matches"""
        if isinstance(self, Ok):
            return self.value == value
        return False

    def is_err(self) -> bool:
        """Returns True if the result is Err"""
        return isinstance(self, Err)

    def is_err_and(self, value: E) -> bool:
        """Returns True if the result is Err and the provided value matches"""
        if isinstance(self, Err):
            return self.value == value
        return False

    def ok(self) -> Optional[T]:
        """Returns the Ok value or None"""
        if isinstance(self, Ok):
            return self.value
        return None

    def err(self) -> Optional[E]:
        """Returns the Err value or None"""
        if isinstance(self, Err):
            return self.value
        return None

    def unwrap(self) -> T:
        """Returns the Ok value or panics"""
        if isinstance(self, Ok):
            return self.value
        panic(f"Called unwrap on an Err value: {cast(Err, self).value}")

    def unwrap_err(self) -> E:
        """Returns the Err value or panics"""
        if isinstance(self, Err):
            return self.value
        panic(f"Called unwrap_err on an Ok value: {cast(Ok, self).value}")

    def unwrap_or(self, default: T) -> T:
        """Returns the Ok value or a default"""
        if isinstance(self, Ok):
            return self.value
        return default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        """Returns the Ok value or computes it from the Err value"""
        if isinstance(self, Ok):
            return self.value
        return op(cast(Err, self).value)

    def expect(self, msg: str) -> T:
        """Returns the Ok value or panics with a custom message"""
        if isinstance(self, Ok):
            return self.value
        panic(f"{msg}: {cast(Err, self).value}")

    def expect_err(self, msg: str) -> E:
        """Returns the Err value or panics with a custom message"""
        if isinstance(self, Err):
            return self.value
        panic(f"{msg}: {cast(Ok, self).value}")

    def map(self, op: Callable[[T], U]) -> Result[U, E]:
        """Maps a Result[T, E] to Result[U, E] by applying a function to the Ok value"""
        if isinstance(self, Ok):
            return Ok(op(self.value))
        return cast(Result[U, E], self)

    def map_err(self, op: Callable[[E], F]) -> Result[T, F]:
        """Maps a Result[T, E] to Result[T, F] by applying a function to the Err value"""
        if isinstance(self, Err):
            return Err(op(self.value))
        return cast(Result[T, F], self)

    def flatten(self: Result[Result[T, E], E]) -> Result[T, E]:
        """Converts from Result[Result[T, E], E] to Result[T, E]"""
        if isinstance(self, Ok) and isinstance(self.value, Result):
            return self.value
        return cast(Result[T, E], self)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Result):
            return False
        if isinstance(self, Ok) and isinstance(other, Ok):
            return self.value == other.value
        if isinstance(self, Err) and isinstance(other, Err):
            return self.value == other.value
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


@dataclass
class Ok(Result[T, E]):
    value: T

    def __init__(self, value: T):
        self.value = value

    def __repr__(self) -> str:
        return f"Ok({self.value})"


@dataclass
class Err(Result[T, E]):
    value: E

    def __init__(self, value: E):
        self.value = value

    def __repr__(self) -> str:
        return f"Err({self.value})"


def resultify(func: Callable[..., T]) -> Callable[..., Result[T, Exception]]:
    """
    Decorator that wraps a function to return a Result instead of raising exceptions.

    Usage:
    ```python
        @resultify
        def divide(a: int, b: int) -> float:
            return a / b

        result = divide(10, 2)  # Ok(5.0)
        result = divide(10, 0)  # Err(ZeroDivisionError(...))
    ```
    """

    def wrapper(*args, **kwargs) -> Result[T, Exception]:
        try:
            value = func(*args, **kwargs)
            if isinstance(value, Result):
                return value
            return Ok(value)
        except Exception as e:
            return Err(e)

    return wrapper
