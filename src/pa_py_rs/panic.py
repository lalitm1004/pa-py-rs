import sys
import threading
import traceback
from typing import NoReturn


def panic(msg: str) -> NoReturn:
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
