**[Home](Home)** ➔ **[Mouse](Mouse)**

<div align = "center">

# **Mouse**

**Native pointer manipulation governed by Bézier-curve physics to simulate authentic human behavior. Perform smooth movements, random wandering, and complex dragging operations while remaining undetected by simple anti-bot mechanisms.**

</div>

---

### **`Mouse().move()`**

Moves the pointer to the specified coordinates smoothly based on the configured physics.

**Description:**

Generates a realistic Bézier curve from the current pointer location to the target. The trajectory, speed, and overshoots are governed by `MousePhysics`.

**Arguments:**

- **`x` (`int`)**
- **`y` (`int`)**

**Returns:**

**`Self`**

**Example:**

```python
Mouse().move(x = 250, y = 500)
```

> [!NOTE]
> Because it uses Bézier curves, the mouse will naturally curve and accelerate/decelerate just like a real human hand.

---

### **`Mouse().click()`**

Clicks the mouse at specified coordinates.

**Description:**

Simulates a physical click (DOWN and UP events) with a customizable, randomized delay in between.

**Arguments:**

- **`x` (`Optional[int]`)**
- **`y` (`Optional[int]`)**
- **`button` (`MouseButton`):** Valid options: "left", "right", "middle". Matching is case-insensitive.
- **`clicks` (`int`):** Must be ≥ 0.

**Returns:**

**`Self`**

**Example:**

```python
Mouse().click(x = 250, y = 500, button = "left", clicks = 1)
```

> [!TIP]
> Passing `x` and `y` automatically moves the pointer to that location before clicking. It is exactly equivalent to `Mouse().move(x, y).click()`.

---

### **`Mouse().double_click()`**

Performs a double click at specified coordinates.

**Description:**

A convenient wrapper around `click()` that forces `clicks = 2`.

**Arguments:**

- **`x` (`Optional[int]`)**
- **`y` (`Optional[int]`)**
- **`button` (`MouseButton`):** Valid options: "left", "right", "middle". Matching is case-insensitive.

**Returns:**

**`Self`**

**Example:**

```python
Mouse().double_click(x = 250, y = 500, button = "left")
```

---

### **`Mouse().right_click()`**

Performs a right click at specified coordinates.

**Description:**

A convenient wrapper around `click()` that forces `button = "right"`.

**Arguments:**

- **`x` (`Optional[int]`)**
- **`y` (`Optional[int]`)**
- **`clicks` (`int`):** Must be ≥ 0.

**Returns:**

**`Self`**

**Example:**

```python
Mouse().right_click(x = 250, y = 500, clicks = 1)
```

---

### **`Mouse().middle_click()`**

Performs a middle click at specified coordinates.

**Description:**

A convenient wrapper around `click()` that forces `button = "middle"`.

**Arguments:**

- **`x` (`Optional[int]`)**
- **`y` (`Optional[int]`)**
- **`clicks` (`int`):** Must be ≥ 0.

**Returns:**

**`Self`**

**Example:**

```python
Mouse().middle_click(x = 250, y = 500, clicks = 1)
```

---

### **`Mouse().hold_click()`**

Holds down a mouse button at specified coordinates.

**Description:**

Sends the physical DOWN signal for the mouse button without releasing it.

**Arguments:**

- **`x` (`Optional[int]`)**
- **`y` (`Optional[int]`)**
- **`button` (`MouseButton`):** Valid options: "left", "right", "middle". Matching is case-insensitive.

**Returns:**

**`Self`**

**Example:**

```python
Mouse().hold_click(x = 250, y = 500, button = "left")
```

> [!WARNING]
> Always ensure you eventually call `release_click()` to avoid leaving the system in a locked state.

---

### **`Mouse().release_click()`**

Releases a previously held mouse button at specified coordinates.

**Description:**

Sends the physical UP signal for the mouse button.

**Arguments:**

- **`x` (`Optional[int]`)**
- **`y` (`Optional[int]`)**
- **`button` (`MouseButton`):** Valid options: "left", "right", "middle". Matching is case-insensitive.

**Returns:**

**`Self`**

**Example:**

```python
Mouse().release_click(x = 250, y = 500, button = "left")
```

---

### **`Mouse().drag_and_drop()`**

Drags an item from start to end coordinates smoothly, based on the configured physics.

**Description:**

Moves to the start coordinates, holds the specified button, waits, smoothly moves to the end coordinates, waits again, and releases the button.

**Arguments:**

- **`start_x` (`int`)**
- **`start_y` (`int`)**
- **`end_x` (`int`)**
- **`end_y` (`int`)**
- **`button` (`MouseButton`):** Valid options: "left", "right", "middle". Matching is case-insensitive.

**Returns:**

**`Self`**

**Example:**

```python
Mouse().drag_and_drop(start_x = 250, start_y = 500, end_x = 750, end_y = 250, button = "left")
```

> [!NOTE]
> Short pauses are automatically inserted before moving and before releasing to simulate a human confirming the grab and drop actions.

---

### **`Mouse().scroll()`**

Scrolls the mouse wheel by the specified amount in the specified direction.

**Description:**

Sends discrete mouse wheel signals to scroll the active window.

**Arguments:**

- **`amount` (`int`):** Must be ≥ 0.
- **`direction` (`ScrollDirection`):** Valid options are "up", "down", "left", or "right". Matching is case-insensitive.

**Returns:**

**`Self`**

**Example:**

```python
Mouse().scroll(amount = 1000, direction = "down")
```

---

### **`Mouse().scroll_until()`**

Scrolls the mouse wheel continuously until a condition is met.

**Description:**

Executes in a loop, scrolling step by step while periodically until either the `condition_function` is met or the `amount`/`timeout` is reached.

**Arguments:**

- **`condition_function` (`Callable[[], bool]`)**
- **`amount` (`int`):** Must be ≥ 0.
- **`direction` (`ScrollDirection`):** Valid options are "up", "down", "left", or "right". Matching is case-insensitive.
- **`timeout` (`float`):** Seconds. Must be ≥ 0.
- **`poll_interval` (`float`):** Seconds. Must be > 0.

**Returns:**

**`Self`**

**Example:**

```python
Mouse().scroll_until(
    condition_function = lambda: KeyboardInfo().is_pressed("shift"),
    amount = 1000,
    direction = "down",
    timeout = 5,
    poll_interval = 0.1
)
```

---

### **`Mouse().wander()`**

Simulates idle mouse wandering by moving the pointer around randomly.

**Description:**

Generates erratic but smooth Bézier movements around a specific region, to keep the computer awake or simulate idle human activity.

**Arguments:**

- **`duration` (`float`):** Seconds. Must be ≥ 0.
- **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
- **`maximum_steps` (`Optional[int]`):** Must be ≥ 0.

**Returns:**

**`Self`**

**Example:**

```python
Mouse().wander(duration = 10, region = (250, 250, 500, 500), maximum_steps = 3)
```

> [!NOTE]
> Although random, the movements generally tend toward the center of the region.

---

### **`Mouse().wander_until()`**

Simulates idle mouse wandering continuously until a condition is met.

**Description:**

Executes the wander logic until the `condition_function` is met or the `maximum_steps`/`timeout` is reached.

**Arguments:**

- **`condition_function` (`Callable[[], bool]`)**
- **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
- **`maximum_steps` (`Optional[int]`):** Must be ≥ 0.
- **`timeout` (`float`):** Seconds. Must be ≥ 0.
- **`poll_interval` (`float`):** Seconds. Must be > 0.

**Returns:**

**`Self`**

**Example:**

```python
Mouse().wander_until(
    condition_function = lambda: KeyboardInfo().is_pressed("shift"),
    region = (250, 250, 500, 500),
    maximum_steps = 3,
    timeout = 5,
    poll_interval = 0.1
)
```

---

### **`MouseInfo().coordinates`**

Gets the current (X, Y) coordinates of the pointer.

**Description:**

Reads the system's pointer position and returns it as a tuple. This is an instantaneous, non-blocking hardware read.

**Returns:**

**`tuple[int, int]`:** Format: (x, y).

**Example:**

```python
x, y = MouseInfo().coordinates
```

---

### **`MouseInfo().x`**

Gets the current X coordinate of the pointer.

**Description:**

Reads the system's pointer position and extracts only the horizontal axis value.

**Returns:**

**`int`**

**Example:**

```python
x = MouseInfo().x
```

---

### **`MouseInfo().y`**

Gets the current Y coordinate of the pointer.

**Description:**

Reads the system's pointer position and extracts only the vertical axis value.

**Returns:**

**`int`**

**Example:**

```python
y = MouseInfo().y
```

---

### **`MouseInfo().pixel_color()`**

Gets the RGB or hexadecimal color of the pixel currently under the pointer.

**Description:**

Takes a micro-screenshot of the exact pixel the mouse is hovering over and extracts its color.

**Arguments:**

- **`format` (`ColorFormat`):** Valid options: "rgb", "hexadecimal". Matching is case-insensitive.

**Returns:**

**`tuple[int, int, int] | str`**

**Example:**

```python
pixel_color = MouseInfo().pixel_color(format = "rgb")
```

---

### **`MouseInfo().pixel_matches_color()`**

Checks if the pixel currently under the pointer matches a specific color.

**Description:**

Takes a micro-screenshot of the exact pixel the mouse is hovering over and compares it with the expected color. If a tolerance is provided, the function will return True if all RGB channels are within the tolerance range.

**Arguments:**

- **`expected_color` (`Union[tuple[int, int, int], str]`):** Format: (R, G, B) or "#RRGGBB".
- **`tolerance` (`float`):** Must be ≥ 0 and ≤ 1.

**Returns:**

**`bool`**

**Example:**

```python
matches = MouseInfo().pixel_matches_color(expected_color = "#FFFFFF", tolerance = 1)
```

---

### **`MouseInfo().on_screen()`**

Checks if the pointer is currently within the bounds of a screen or region.

**Description:**

Verifies if the current mouse coordinates fall inside the designated screen or region. Useful for multi-monitor setups.

**Arguments:**

- **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
- **`monitor_index` (`int`)**

**Returns:**

**`bool`**

**Example:**

```python
is_pointer_on_screen = MouseInfo().on_screen(region = [250, 250, 500, 500], monitor_index = 0)
```