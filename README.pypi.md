[![PyPI version info](https://img.shields.io/pypi/v/pa-py-rs.svg?style=for-the-badge&logo=pypi&color=yellowgreen&logoColor=white)](https://pypi.python.org/pypi/pa-py-rs)
[![PyPI supported Python versions](https://img.shields.io/pypi/pyversions/pa-py-rs.svg?style=for-the-badge&logo=python&logoColor=white)](https://pypi.python.org/pypi/pa-py-rs)

# Key Features
- Result Type: Rust-style `Result[T, E]` for explicit error handling without exceptions
- Ok/Err Variants: Type-safe success and error cases with pattern matching methods
- Panic Mechanism: Rust-like `panic()` for unrecoverable errors with detailed stack traces
- Decorator Utilities: Convert existing functions to return Results with `@resultify` and `@resultify_catch_only`
- Chainable Operations: Functional methods like `map`, `map_err`, `unwrap_or`, and more
- Fully Typed: Complete type hints for excellent IDE support and type checking

# Installation
```bash
# using pip
pip install pa-py-rs

# using uv
uv add pa-py-rs
```
> *NOTE: Python 3.7 or higher is required*

# Examples
## Result
### Basic Result Usage
```python
from pa_py_rs import Result, Ok, Err

def divide(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)

result = divide(10, 2)
print(result)   # Ok(5.0)
if result.is_ok():
    print(f"Success: {result.unwrap()}")    # Success: 5.0

result = divide(10, 0)
print(result)   # Err(Division by zero)
if result.is_err():
    print(f"Error: {result.unwrap_err()}")  # Error: Division by zero
```

### Using decorators
```python
from pa_py_rs import resultify, resultify_catch_only

# Convert any function to return Result
# Automatically catch errors and wrap in Err(...)
@resultify
def parse_int(value: str) -> int:
    return int(value)

result = parse_int("123")   # Ok(123)
result = parse_int("abc")   # Err(...)

# For functions already returning Result
# Automatically catch errors and wrap in Err(...)
@resultify_catch_only
def divide(a: float, b: float) -> Result[float, str]:
    return Ok(a / b)

result = divide(10, 2)  # Ok(5.0)
result = divide(10, 0)  # Err("cannot divide by zero")
```

### Chaining Operations
```python
from pa_py_rs import Ok, Err

result = Err("error").unwrap_or(0)
print(result)   # 0

result = (Ok(10)
    .map(lambda x: x * 2)
    .map(lambda x: x + 5)
    .unwrap())
print(result)   # 25
```