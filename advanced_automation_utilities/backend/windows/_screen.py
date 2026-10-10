from ..._utilities import _validate_between_range
import ctypes
import ctypes.wintypes
lazy import asyncio
lazy import mss
lazy import numpy
lazy import cv2
lazy from winrt.windows.graphics.imaging import SoftwareBitmap, BitmapPixelFormat, BitmapAlphaMode
lazy from winrt.windows.storage.streams import DataWriter
lazy from winrt.windows.media.ocr import OcrEngine

_SPI_GETWORKAREA = 48

def _get_screen_resolution():
    with mss.mss() as screen_capture_tool:
        monitor = screen_capture_tool.monitors[1]
        return monitor["width"], monitor["height"]

def _get_pixel_color(x, y):
    with mss.mss() as screen_capture_tool:
        virtual = screen_capture_tool.monitors[0]
        _validate_between_range(virtual["left"], virtual["left"] + virtual["width"] - 1, x = x)
        _validate_between_range(virtual["top"], virtual["top"] + virtual["height"] - 1, y = y)
    device_context = ctypes.windll.user32.GetDC(0)
    color = ctypes.windll.gdi32.GetPixel(device_context, x, y)
    ctypes.windll.user32.ReleaseDC(0, device_context)
    r = color & 0xFF
    g = (color >> 8) & 0xFF
    b = (color >> 16) & 0xFF
    return (r, g, b)

def _get_work_area():
    rectangle = ctypes.wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(_SPI_GETWORKAREA, 0, ctypes.byref(rectangle), 0)
    return rectangle.left, rectangle.top, rectangle.right, rectangle.bottom

def _take_screenshot(region = None, monitor_index = 0, save_path = None):
    with mss.mss() as screen_capture_tool:
        if region is None: screen = screen_capture_tool.monitors[monitor_index]
        else:
            left, top, right, bottom = region
            screen = {
                "left": int(left),
                "top": int(top),
                "width": int(right - left),
                "height": int(bottom - top)
            }
        screenshot = screen_capture_tool.grab(screen)
    if save_path is not None:
        image = numpy.array(screenshot)
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        cv2.imwrite(save_path, image)
    return screenshot

def _adjust_coordinates_for_region(x, y, region, monitor_index = 0):
    if region is not None:
        x += region[0]
        y += region[1]
    elif monitor_index != 0:
        with mss.mss() as screen_capture_tool:
            monitor = screen_capture_tool.monitors[monitor_index]
            x += monitor["left"]
            y += monitor["top"]
    return int(x), int(y)

def _locate_image(image_path, confidence, limit, region, monitor_index):
    with open(image_path, "rb") as file:
        image_array = numpy.frombuffer(file.read(), numpy.uint8)
    template = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if template is None:
        raise ValueError(
            f"Failed to read image at \"{image_path}\". Ensure it is a valid image file."
        )
    screenshot = _take_screenshot(region, monitor_index)
    image = numpy.array(screenshot)
    image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    height, width = template.shape[:2]
    if limit == 1:
        _, maximum_value, _, maximum_location = cv2.minMaxLoc(result)
        if maximum_value >= confidence:
            x = maximum_location[0] + width / 2
            y = maximum_location[1] + height / 2
            return _adjust_coordinates_for_region(x, y, region, monitor_index)
        return None, None
    else:
        locations = numpy.where(result >= confidence)
        locations = list(zip(*locations[::-1]))
        matches = []
        for location in locations:
            x = location[0] + width / 2
            y = location[1] + height / 2
            matches.append(_adjust_coordinates_for_region(x, y, region, monitor_index))
            if limit > 0 and len(matches) >= limit: break
        return matches

def _run_ocr_on_region(region = None, monitor_index = 0):
    screenshot = _take_screenshot(region, monitor_index)
    width = screenshot.width
    height = screenshot.height
    image = numpy.array(screenshot, dtype = numpy.uint8)
    software_bitmap = SoftwareBitmap(
        BitmapPixelFormat.BGRA8, width, height, BitmapAlphaMode.PREMULTIPLIED
    )
    data_writer = DataWriter()
    data_writer.write_bytes(image.tobytes())
    buffer = data_writer.detach_buffer()
    software_bitmap.copy_from_buffer(buffer)
    engine = OcrEngine.try_create_from_user_profile_languages()
    if engine is None:
        raise SystemError(
            "Windows OCR engine could not be initialized. Please check your language settings."
        )

    async def recognize(): return await engine.recognize_async(software_bitmap)

    return asyncio.run(recognize())