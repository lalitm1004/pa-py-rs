import sys
import threading
import traceback
from typing import NoReturn


def panic(msg: str) -> NoReturn:
    """
    Terminates the program immediately after printing a structured panic report.

    This function is intended as a hard failure mechanism similar to Rust's
    `panic!()`. It prints a detailed error message to standard error, including:

    - the name of the current thread
    - the provided panic message
    - the source location where `panic()` was invoked
    - a formatted stack backtrace of the call frames leading to the panic

    After emitting the panic report, the function exits the process with
    `sys.exit(1)` and never returns.

    Parameters:
        msg (str):
            A human-readable explanation of the failure condition.

    Notes:
        - `panic()` is not intended for recoverable errors; use exception handling
          or a `Result`-style abstraction for that.
        - Because this function terminates the entire process, it should be used
          sparingly and only for unrecoverable, logic-error conditions.
    """
    thread_name = threading.current_thread().name

    stack = traceback.extract_stack()[:-1]
    if stack:
        frame = stack[-1]
        location = f"{frame.filename}:{frame.lineno}:{frame.colno}"
    else:
        location = "<unknown>"

    print(f"thread '{thread_name}' panicked at '{msg}', '{location}'", file=sys.stderr)
    print("stack backtrace:", file=sys.stderr)
    for i, frame in enumerate(stack):
        print(
            f"\t{i:>2}: {frame.filename}:{frame.lineno} - {frame.name}", file=sys.stderr
        )

    sys.exit(1)


if __name__ == "__main__":
    panic("test panic")
