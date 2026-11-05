import time

class TimingInfo:
    """
    **`TimingInfo`:** Provides high-resolution time measurements.

    **Description:**

    Class that provides instantaneous timing information.
    """
    @property
    def time(self) -> float:
        """
        **`TimingInfo().time`:** Gets the current time in seconds.

        **Description:**

        Utilizes the high-resolution performance counter (`time.perf_counter`) to get the current time in seconds.

        **Returns:**

        **`float`**

        **Example:**

        ```python
        current_time = TimingInfo().time
        ```
        """
        return time.perf_counter()