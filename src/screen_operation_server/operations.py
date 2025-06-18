import base64
import io
import platform
from typing import Any, Dict, List

import mss
from PIL import Image

# Platform-specific imports
SYSTEM = platform.system()
if SYSTEM == "Linux":
    try:
        from Xlib import X, display
    except ImportError:
        # This allows the program to be imported on systems without Xlib.
        pass
elif SYSTEM == "Windows":
    try:
        import pywintypes
        import win32gui
    except ImportError:
        pass
elif SYSTEM == "Darwin":
    try:
        from AppKit import NSWorkspace
        from Quartz import (
            CGWindowListCopyWindowInfo,
            kCGNullWindowID,
            kCGWindowListOptionOnScreenOnly,
            kCGWindowListOptionIncludingWindow
        )
    except ImportError:
        pass


def _capture_to_base64(sct: mss.mss, monitor: Dict) -> Dict[str, str]:
    """Captures a region and returns it as a base64 encoded PNG."""
    sct_img = sct.grab(monitor)
    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return {"content": img_str, "mime_type": "image/png"}


def get_screen_info() -> Dict[str, Any]:
    """Gets information about all connected displays."""
    with mss.mss() as sct:
        # sct.monitors[0] is a virtual monitor of all screens combined
        monitors = sct.monitors
        return {
            "monitor_count": len(monitors) -1 if len(monitors) > 1 else 1,
            "monitors": [
                {
                    "id": i,
                    "width": m["width"],
                    "height": m["height"],
                    "top": m["top"],
                    "left": m["left"],
                }
                for i, m in enumerate(monitors)
            ],
        }


def capture_screen_by_number(monitor_number: int) -> Dict[str, str]:
    """Captures a screenshot of a specific monitor."""
    with mss.mss() as sct:
        try:
            monitor = sct.monitors[monitor_number]
            return _capture_to_base64(sct, monitor)
        except IndexError:
            raise ValueError(f"Monitor {monitor_number} not found.")


def capture_all_screens() -> Dict[str, str]:
    """Captures all screens and stitches them into a single image."""
    with mss.mss() as sct:
        # Skip the first monitor which is the combined view of all monitors
        monitors_to_capture = sct.monitors[1:]

        # If only one monitor, capture it
        if not monitors_to_capture:
            return _capture_to_base64(sct, sct.monitors[0])

        images = [
            Image.frombytes("RGB", sct.grab(m).size, sct.grab(m).bgra, "raw", "BGRX")
            for m in monitors_to_capture
        ]

        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)

        stitched_image = Image.new("RGB", (total_width, max_height))

        x_offset = 0
        for img in images:
            stitched_image.paste(img, (x_offset, 0))
            x_offset += img.width

        buffer = io.BytesIO()
        stitched_image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return {"content": img_str, "mime_type": "image/png"}


def get_window_list() -> List[Dict[str, Any]]:
    """Gets a list of all visible windows."""
    if SYSTEM == "Linux":
        return _get_window_list_linux()
    elif SYSTEM == "Windows":
        return _get_window_list_windows()
    elif SYSTEM == "Darwin":
        return _get_window_list_macos()
    else:
        raise NotImplementedError(f"get_window_list is not implemented for {SYSTEM}")


def capture_window(window_id: int) -> Dict[str, str]:
    """Captures a screenshot of a specific window by its ID."""
    if SYSTEM == "Linux":
        return _capture_window_linux(window_id)
    elif SYSTEM == "Windows":
        return _capture_window_windows(window_id)
    elif SYSTEM == "Darwin":
        return _capture_window_macos(window_id)
    else:
        raise NotImplementedError(f"capture_window is not implemented for {SYSTEM}")


# --- Platform-specific implementations ---


def _get_window_list_windows() -> List[Dict[str, Any]]:
    windows = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            rect = win32gui.GetWindowRect(hwnd)
            x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
            if w > 0 and h > 0:
                windows.append(
                    {"id": hwnd, "title": win32gui.GetWindowText(hwnd), "x": x, "y": y, "width": w, "height": h}
                )
    win32gui.EnumWindows(callback, None)
    return windows


def _capture_window_windows(window_id: int) -> Dict[str, str]:
    try:
        rect = win32gui.GetWindowRect(window_id)
    except pywintypes.error:
        raise ValueError(f"Window with ID {window_id} not found.")

    monitor = {"top": rect[1], "left": rect[0], "width": rect[2] - rect[0], "height": rect[3] - rect[1]}
    with mss.mss() as sct:
        return _capture_to_base64(sct, monitor)


def _get_window_list_linux() -> List[Dict[str, Any]]:
    d = display.Display()
    root = d.screen().root
    window_ids = root.get_full_property(d.intern_atom("_NET_CLIENT_LIST"), X.AnyPropertyType).value
    windows = []
    for window_id in window_ids:
        try:
            window = d.create_resource_object("window", window_id)
            attrs = window.get_attributes()
            if attrs.map_state != X.IsViewable:
                continue

            title_prop = window.get_full_property(d.intern_atom("_NET_WM_NAME"), d.intern_atom("UTF8_STRING"))
            title = title_prop.value.decode("utf-8") if title_prop else ""
            if not title:
                title_prop = window.get_full_property(X.WM_NAME, X.AnyPropertyType)
                title = title_prop.value.decode("latin-1") if title_prop else ""

            if title:
                geom = window.get_geometry()
                coords = root.translate_coords(window, 0, 0)
                windows.append(
                    {"id": window_id, "title": title, "x": coords.x, "y": coords.y, "width": geom.width, "height": geom.height}
                )
        except Exception:
            continue
    return windows


def _capture_window_linux(window_id: int) -> Dict[str, str]:
    try:
        d = display.Display()
        root = d.screen().root
        window = d.create_resource_object("window", window_id)
        geom = window.get_geometry()
        coords = root.translate_coords(window, 0, 0)
    except Exception:
        raise ValueError(f"Window with ID {window_id} not found.")

    monitor = {"top": coords.y, "left": coords.x, "width": geom.width, "height": geom.height}
    with mss.mss() as sct:
        return _capture_to_base64(sct, monitor)


def _get_window_list_macos() -> List[Dict[str, Any]]:
    options = kCGWindowListOptionOnScreenOnly
    window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
    windows = []
    for window in window_list:
        if window.get("kCGWindowLayer") == 0 and window.get("kCGWindowOwnerName"):
            bounds = window.get("kCGWindowBounds", {})
            windows.append({
                "id": window.get("kCGWindowNumber"),
                "title": f'{window.get("kCGWindowOwnerName")} - {window.get("kCGWindowName", "")}',
                "x": int(bounds.get("X", 0)),
                "y": int(bounds.get("Y", 0)),
                "width": int(bounds.get("Width", 0)),
                "height": int(bounds.get("Height", 0)),
            })
    return windows


def _capture_window_macos(window_id: int) -> Dict[str, str]:
    options = kCGWindowListOptionIncludingWindow
    window_list = CGWindowListCopyWindowInfo(options, window_id)
    if not window_list:
        raise ValueError(f"Window with ID {window_id} not found.")

    bounds = window_list[0].get("kCGWindowBounds", {})
    monitor = {
        "left": int(bounds.get("X", 0)),
        "top": int(bounds.get("Y", 0)),
        "width": int(bounds.get("Width", 0)),
        "height": int(bounds.get("Height", 0)),
    }
    with mss.mss() as sct:
        return _capture_to_base64(sct, monitor)
