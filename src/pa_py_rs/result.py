from __future__ import annotations
from typing import Callable, Generic, Optional, TypeVar, Union, cast

from pa_py_rs.panic import panic

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")
F = TypeVar("F")


class Result(Generic[T, E]):
    __slots__ = ("value", "_is_ok")

    def __init__(self):
        raise NotImplementedError("Use Ok() or Err() to create Result instance")

    def is_ok(self) -> bool:
        """Returns True if the result is Ok"""
        return self._is_ok

    def is_ok_and(self, value: T) -> bool:
        """Returns True if the result is Ok and the provided value matches"""
        if self._is_ok:
            return self.value == value
        return False

    def is_err(self) -> bool:
        """Returns True if the result is Err"""
        return not self._is_ok

    def is_err_and(self, value: E) -> bool:
        """Returns True if the result is Err and the provided value matches"""
        if not self._is_ok:
            return self.value == value
        return False

    def ok(self) -> Optional[T]:
        """Returns the Ok value or None"""
        if self._is_ok:
            return self.value
        return None

    def err(self) -> Optional[E]:
        """Returns the Err value or None"""
        if not self._is_ok:
            return self.value
        return None

    def unwrap(self) -> T:
        """Returns the Ok value or panics"""
        if self._is_ok:
            return self.value
        panic(f"Called unwrap on an Err value: {cast(Err, self).value}")

    def unwrap_err(self) -> E:
        """Returns the Err value or panics"""
        if not self._is_ok:
            return self.value
        panic(f"Called unwrap_err on an Ok value: {cast(Ok, self).value}")

    def unwrap_or(self, default: T) -> T:
        """Returns the Ok value or a default"""
        if self._is_ok:
            return self.value
        return default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        """Returns the Ok value or computes it from the Err value"""
        if self._is_ok:
            return self.value
        return op(self.value)

    def expect(self, msg: str) -> T:
        """Returns the Ok value or panics with a custom message"""
        if self._is_ok:
            return self.value
        panic(f"{msg}: {cast(Err, self).value}")

    def expect_err(self, msg: str) -> E:
        """Returns the Err value or panics with a custom message"""
        if not self._is_ok:
            return self.value
        panic(f"{msg}: {cast(Ok, self).value}")

    def map(self, op: Callable[[T], U]) -> Result[U, E]:
        """Maps a Result[T, E] to Result[U, E] by applying a function to the Ok value"""
        if self._is_ok:
            return Ok(op(self.value))
        return cast(Result[U, E], self)

    def map_err(self, op: Callable[[E], F]) -> Result[T, F]:
        """Maps a Result[T, E] to Result[T, F] by applying a function to the Err value"""
        if not self._is_ok:
            return Err(op(self.value))
        return cast(Result[T, F], self)

    def flatten(self: Result[Result[T, E], E]) -> Result[T, E]:
        """Converts from Result[Result[T, E], E] to Result[T, E]"""
        if self._is_ok and isinstance(self.value, Result):
            return self.value
        return cast(Result[T, E], self)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Result):
            return False
        if self._is_ok and other._is_ok:
            return self.value == other.value
        if not self._is_ok and not other._is_ok:
            return self.value == other.value
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class Ok(Result[T, E]):
    __slots__ = ()

    def __init__(self, value: T):
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "_is_ok", True)

    def __repr__(self) -> str:
        return f"Ok({self.value})"


class Err(Result[T, E]):
    __slots__ = ()

    def __init__(self, value: E):
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "_is_ok", False)

    def __repr__(self) -> str:
        return f"Err({self.value})"


def resultify(func: Callable[..., T]) -> Callable[..., Result[T, Exception]]:
    """
    Decorator that converts a regular function into one that returns a Result

    The wrapped function's return value is placed inside `Ok(...)`
    If the function raises any exception, it is caught and wrapped in `Err(Exception)`

    **NOTE: This decorator is intended only for functions whose return type is not
    already a Result. Applying it to a function that returns `Result[T, E]`
    will cause the Result to be wrapped again as `Ok(Result(...))`, which is
    almost always undesirable**

    Example:
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
            return Ok(func(*args, **kwargs))
        except Exception as e:
            return Err(e)

    return wrapper


def resultify_catch_only(
    func: Callable[..., Result[T, E]],
) -> Callable[..., Result[T, Union[E, Exception]]]:
    """
    Decorator that wraps a function which already returns a `Result`, ensuring that
    unexpected exceptions are converted into Err values while preserving the function's original `Result` type.
    If the wrapped function raises any exception instead of returning an `Err` value, that exception is caught and wrapped into
    `Err(exception)` widening the error type to `E | Exception`

    **NOTE: This decorator must only be applied to functions that already and reliably return a `Result`.
    It does not wrap raw return values. If used on a function that does not return a `Result`, the raw value will be passed
    through unchanged and treated as if it were a `Result`, which is incorrect and type-unsafe.
    For non-Result-returning functions, use `resultify` instead**

    Example:
    ```python
    @resultify_catch_only
    def divide_unsafe(a: float, b: float) -> Result[float, str]:
        return Ok(a / b)

    result = divide(10, 2)  # Ok(5.0)
    result = divide(10, 0)  # Err(ZeroDivisionError(...))
    ```
    """

    def wrapper(*args, **kwargs) -> Result[T, Union[E, Exception]]:
        try:
            return cast(Result[T, Union[E, Exception]], func(*args, **kwargs))
        except Exception as e:
            return Err(e)

    return wrapper
