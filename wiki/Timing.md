**[Home](Home)** ➔ **[Timing](Timing)**

<div align = "center">

# **Timing**

**Precise delays, chronometers, and condition-based execution flow. Use this module to introduce smart waits that continuously poll for conditions, simulate human-like random pauses, or precisely benchmark the execution time of your functions.**

</div>

---

### **`Timing().wait()`**

Pauses execution for an exact amount of seconds.

**Description:**

Pauses execution for an exact amount of seconds. It acts as a safe, responsive wrapper around standard sleep mechanisms, ensuring that long pauses can still be instantly interrupted if the global kill switch is triggered.

**Arguments:**

- **`duration` (`float`):** Seconds. Must be ≥ 0.

**Returns:**

**`None`**

**Example:**

```python
Timing().wait(duration = 2.5)
```

> [!NOTE]
> This internally uses the global `KILL_SWITCH_EVENT`, meaning if the Kill Switch is triggered during a wait, the wait is aborted instantly.

---

### **`Timing().wait_random()`**

Pauses execution for a random duration between two limits.

**Description:**

Pauses execution for a random duration between two limits. This is particularly useful for simulating human unpredictability and preventing strict pattern recognition in automated tasks.

**Arguments:**

- **`minimum_duration` (`float`):** Seconds. Must be ≥ 0.
- **`maximum_duration` (`float`):** Seconds. Must be ≥ 0.

**Returns:**

**`None`**

**Example:**

```python
Timing().wait_random(minimum_duration = 1, maximum_duration = 3)
```

---

### **`Timing().wait_until()`**

Pauses execution until a given condition function is met.

**Description:**

Continuously polls the condition function at a specified interval until is met or the timeout is reached.

**Arguments:**

- **`condition_function` (`Callable[[], bool]`)**
- **`timeout` (`float`):** Seconds. Must be ≥ 0.
- **`poll_interval` (`float`):** Seconds. Must be > 0.

**Returns:**

**`bool`**

**Example:**

```python
Timing().wait_until(
    condition_function = lambda: KeyboardInfo().is_pressed("shift"),
    timeout = 10,
    poll_interval = 0.1
)
```

---

### **`TimingInfo().time`**

Gets the current time in seconds.

**Description:**

Utilizes the high-resolution performance counter (`time.perf_counter`) to get the current time in seconds.

**Returns:**

**`float`**

**Example:**

```python
current_time = TimingInfo().time
```

---

### **`@measure_time`**

A decorator to automatically measure and print the execution time of any function.

**Description:**

Place this above your function definitions to measure their execution time.

**Arguments:**

- **`function` (`Callable`)**

**Returns:**

**`Callable`**

**Example:**

```python
@measure_time
def heavy_task(): pass
```