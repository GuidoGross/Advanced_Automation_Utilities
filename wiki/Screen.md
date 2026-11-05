**[Home](Home)** ➔ **[Screen](Screen)**

<div align = "center">

# **Screen**

**Advanced computer vision leveraging OpenCV and native Windows OCR. Read text from specific regions, locate UI elements via template matching, and interact with pixel-perfect accuracy across multi-monitor setups without requiring external cloud services.**

</div>

---

### **`Screen().take_screenshot()`**

Takes a screenshot of the screen or a specific region.

**Description:**

Takes a blazing-fast screenshot using `mss`. Optionally saves it to a file.

**Arguments:**

- **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
- **`monitor_index` (`int`)**
- **`save_path` (`Optional[str]`):** Must be a valid file path.

**Returns:**

**`mss.base.ScreenShot`**

**Example:**

```python
screenshot = Screen().take_screenshot(
    region = (250, 250, 500, 500),
    monitor_index = 0,
    save_path = "screenshot.png"
)
```

---

### **`Screen().locate_image()`**

Searches for a template image on the screen and returns its central coordinates.

**Description:**

Takes a fast screenshot and uses OpenCV Template Matching (`TM_CCOEFF_NORMED`) to find the image in the specified region.

**Arguments:**

- **`image_path` (`str`):** Must be a valid file path.
- **`confidence` (`float`):** Must be ≥ 0 and ≤ 1.
- **`limit` (`int`):** Must be ≥ 0.
- **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
- **`monitor_index` (`int`)**

**Returns:**

**`Union[tuple[Optional[int], Optional[int]], list[tuple[int, int]]]`:** Format: (x, y) or a list of them.

**Example:**

```python
x, y = Screen().locate_image(
    image_path = "button.png",
    confidence = 0.9,
    limit = 1,
    region = (250, 250, 500, 500),
    monitor_index = 0
)
```

---

### **`Screen().locate_text()`**

Uses OCR to find specific text on the screen and returns its central coordinates.

**Description:**

Leverages the blazing-fast native Windows OCR API to find the location of specific text within the specified region.

**Arguments:**

- **`text` (`str`)**
- **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
- **`exact_match` (`bool`)**
- **`monitor_index` (`int`)**

**Returns:**

**`tuple[Optional[int], Optional[int]]`**

**Example:**

```python
x, y = Screen().locate_text(
    text = "Submit",
    region = (250, 250, 500, 500),
    exact_match = True,
    monitor_index = 0
)
```

---

### **`Screen().read_text()`**

Uses OCR to extract all readable text from the screen or a specific region.

**Description:**

Leverages the blazing-fast native Windows OCR API to extract all readable text from the screen or a specific region.

**Arguments:**

- **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
- **`monitor_index` (`int`)**

**Returns:**

**`str`**

**Example:**

```python
text = Screen().read_text(region = (250, 250, 500, 500), monitor_index = 0)
```

---

### **`ScreenInfo().resolution`**

Gets the resolution of the primary screen.

**Description:**

Returns the resolution of the primary screen as a tuple.

**Returns:**

**`tuple[int, int]`:** Format: (width, height).

**Example:**

```python
width, height = ScreenInfo().resolution
```

---

### **`ScreenInfo().width`**

Gets the width of the primary screen.

**Description:**

Returns only the width of the primary screen as an integer.

**Returns:**

**`int`**

**Example:**

```python
width = ScreenInfo().width
```

---

### **`ScreenInfo().height`**

Gets the height of the primary screen.

**Description:**

Returns only the height of the primary screen as an integer.

**Returns:**

**`int`**

**Example:**

```python
height = ScreenInfo().height
```

---

### **`ScreenInfo().pixel_color()`**

Gets the RGB or hexadecimal color of a specific pixel coordinate.

**Description:**

Returns the color of the pixel at the specified coordinates on RGB or hexadecimal format.

**Arguments:**

- **`x` (`int`)**
- **`y` (`int`)**
- **`format` (`ColorFormat`):** Valid options: "rgb", "hexadecimal". Matching is case-insensitive.

**Returns:**

**`Union[tuple[int, int, int], str]`:** Format: (R, G, B) for "rgb" or "#RRGGBB" for "hexadecimal".

**Example:**

```python
pixel_color = ScreenInfo().pixel_color(x = 250, y = 500, format = "hexadecimal")
```

---

### **`ScreenInfo().pixel_matches_color()`**

Checks if a pixel matches a specific color with a given tolerance.

**Description:**

Compares the color of the pixel at the specified coordinates with the expected color. If a tolerance is provided, the function will return True if all RGB channels are within the tolerance range.

**Arguments:**

- **`x` (`int`)**
- **`y` (`int`)**
- **`expected_color` (`Union[tuple[int, int, int], str]`):** Format: (R, G, B) or "#RRGGBB".
- **`tolerance` (`float`):** Must be ≥ 0 and ≤ 1.

**Returns:**

**`bool`**

**Example:**

```python
matches = ScreenInfo().pixel_matches_color(
    x = 250, y = 500, expected_color = "#FFFFFF", tolerance = 1
)
```

---

### **`ScreenInfo().on_screen()`**

Checks if the given coordinates are within the bounds of a screen or region.

**Description:**

Verifies if the specified (x, y) coordinates fall inside the designated screen or region.

**Arguments:**

- **`x` (`int`)**
- **`y` (`int`)**
- **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
- **`monitor_index` (`int`)**

**Returns:**

**`bool`**

**Example:**

```python
is_visible = ScreenInfo().on_screen(x = 250, y = 500, monitor_index = 0)
```

---

### **`ScreenInfo().work_area`**

Gets the primary screen's work area, excluding the taskbar.

**Description:**

Returns the boundaries of the primary screen's usable work area. This excludes the Windows taskbar and any other docked desktop toolbars, providing the exact coordinates of the space available for applications and windows.

**Returns:**

**`tuple[int, int, int, int]`:** Format: (left, top, right, bottom).

**Example:**

```python
left, top, right, bottom = ScreenInfo().work_area
```