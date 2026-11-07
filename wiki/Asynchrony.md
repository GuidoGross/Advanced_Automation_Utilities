**[Home](Home)** ➔ **[Asynchrony](Asynchrony)**

<div align = "center">

# **Asynchrony**

**This library features a powerful Context Manager-based asynchronous execution system. All hardware-bound actions, such as Mouse, Keyboard, Screen, Sound, or System operations, can be seamlessly queued and executed in the background. This architecture allows you to perform heavy operations concurrently without blocking your main script's logic.**

</div>

## **Introduction**

Most core controllers (`Mouse`, `Keyboard`, `Screen`, `Sound`, `System`) inherit from a queueable controller base. This means any action they provide can be executed either synchronously (blocking the main thread) or asynchronously (queued in a background worker thread).

To execute actions asynchronously, simply wrap them inside a `with controller.asynchronous() as controller_task:` block. All actions invoked on that controller within the block will be queued and executed sequentially in the background.

> [!TIP]
> All actions return `Self`, meaning they can be fluidly chained together. For instance, `Mouse().move(x = 250, y = 500).click()` queues both actions sequentially within the same background task.

**Example:**

```python
mouse = Mouse()
with mouse.asynchronous() as mouse_task:
    mouse.move(x = 250, y = 500)
    mouse.scroll(amount = 1000, direction = "down")
```

## **Embedded timing actions**

Because every controller is queueable, they all inherit basic timing capabilities. These allow you to inject precise pauses directly into your asynchronous chains.

### **`wait()`**

Pauses execution for an exact duration.

**Description:**

Pauses execution for an exact amount of seconds. Can be chained and queued asynchronously.

**Arguments:**

- **`duration` (`float`):** Seconds. Must be ≥ 0.

**Returns:**

**`Self`**

**Example:**

```python
with mouse.asynchronous() as mouse_task: mouse.wait(duration = 2.5)
```

### **`wait_random()`**

Pauses execution for a random duration within two limits.

**Description:**

Pauses execution for a random duration between two limits. Can be chained and queued asynchronously.

**Arguments:**

- **`minimum_duration` (`float`):** Seconds. Must be ≥ 0.
- **`maximum_duration` (`float`):** Seconds. Must be ≥ 0.

**Returns:**

**`Self`**

**Example:**

```python
with mouse.asynchronous() as mouse_task:
    mouse.wait_random(minimum_duration = 1, maximum_duration = 3)
```

### **`wait_until()`**

Pauses execution until a condition evaluates to True.

**Description:**

Pauses execution until a given function or lambda condition evaluates to True. Can be chained and queued asynchronously.

**Arguments:**

- **`condition_function` (`Callable[[], bool]`)**
- **`timeout` (`float`):** Seconds. Must be ≥ 0.
- **`poll_interval` (`float`):** Seconds. Must be > 0.

**Returns:**

**`Self`**

**Example:**

```python
with mouse.asynchronous() as mouse_task:
    mouse.wait_until(
        condition_function = lambda: KeyboardInfo().is_pressed(key = "shift"),
        timeout = 5,
        poll_interval = 0.1
    )
```

## **Task Management**

When you use the `asynchronous()` context manager, it returns a `Task` object. This object allows you to monitor and control the background thread.

### **`Task().wait()`**

Blocks until the task completes, is cancelled, or timeout expires.

**Description:**

Waits for every queued action to finish, for cancellation to stop the sequence, or until timeout seconds elapse. If an action raises an exception, the same exception is raised in the thread calling this method.

**Arguments:**

- **`timeout` (`Optional[float]`):** Maximum seconds to wait. Must be ≥ 0.

**Returns:**

**`bool`**

**Example:**

```python
with mouse.asynchronous() as mouse_task: mouse.move(x = 500, y = 500)
completed = mouse_task.wait(timeout = 5)
```

### **`Task().cancel()`**

Cancels a task that has not started or is still running.

**Description:**

Requests cancellation of the queued sequence. Actions that have not started are skipped, and a running action receives the task's cancellation event so it can stop cooperatively.

**Returns:**

**`None`**

**Example:**

```python
with mouse.asynchronous() as mouse_task: mouse.move(x = 250, y = 500)
image_found = screen.locate_image(
    image_path = "error.png",
    confidence = 0.9,
    region = [250, 250, 500, 500],
    monitor_index = 0
)
if image_found: mouse_task.cancel()
```

### **`Task().is_done`**

Checks whether the task is complete or cancelled.

**Description:**

Returns True after the queued sequence has stopped, whether it completed, was cancelled, or ended because an action raised an exception.

**Returns:**

**`bool`**

**Example:**

```python
with keyboard.asynchronous() as keyboard_task: keyboard.write("Hello, world!")
with mouse.asynchronous() as mouse_task:
    mouse.wander_until(condition_function = lambda: keyboard_task.is_done)
```

## **Returning Results**

To fetch the return value(s) of your asynchronous actions, you can use the `last_result` or `results` properties directly on the returned `Task` object once it finishes executing.

> [!TIP]
> Both `last_result` and `results` are also available on the controller object itself. This is extremely useful for fetching results at the end of a synchronous chain.

### **`Task().last_result`**

**Description:**

Stores the return value of the very last action executed in the task.

**Example:**

```python
with screen.asynchronous() as screen_task:
    screen.locate_image(
        image_path = "button.png",
        confidence = 0.9,
        limit = 1,
        region = (250, 250, 500, 500),
        monitor_index = 0
    )
    screen.locate_text(
        text = "Submit",
        region = (250, 250, 500, 500),
        exact_match = True,
        monitor_index = 0
    )
result = screen_task.last_result
```

### **`Task().results`**

**Description:**

A list containing the return values of all actions executed in the task, in the order they were queued.

**Example:**

```python
with screen.asynchronous() as screen_task:
    screen.locate_image(
        image_path = "button.png",
        confidence = 0.9,
        limit = 1,
        region = (250, 250, 500, 500),
        monitor_index = 0
    )
    screen.locate_text(
        text = "Submit",
        region = (250, 250, 500, 500),
        exact_match = True,
        monitor_index = 0
    )
results = screen_task.results
```