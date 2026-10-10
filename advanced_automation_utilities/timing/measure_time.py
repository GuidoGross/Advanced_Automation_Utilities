from .timing_info import TimingInfo
from functools import wraps
from typing import Callable
lazy from tui_utilities import print, decimal_format

def measure_time(function: Callable) -> Callable:
    """
    **Description:**

    A decorator to automatically measure and print the execution time of any function.

    **Arguments:**

    - **`function` (`Callable`)**

    **Returns:**

    **`Callable`**

    **Example:**

    ```python
    @measure_time
    def heavy_task(): pass
    ```
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        timing_info = TimingInfo()
        start_time = timing_info.time
        result = function(*args, **kwargs)
        end_time = timing_info.time
        print([
            ("Execution of ", {}),
            (f"{function.__name__}()", {"color": "#00bfff"}),
            (" finished in ", {}),
            (f"{decimal_format((end_time - start_time), decimals = 5)}s", {"color": "#00bfff"})
        ], alignment = "center")
        return result

    return wrapper