import asyncio
import platform
from typing import Any, Dict, List

import mcp
from mcp.server import InitializationOptions, NotificationOptions, Server

from . import operations

# Create the MCP server instance
mcp_server = Server("screen-operation-server", "v0.1.0")


@mcp_server.tool()
async def get_screen_info() -> Dict[str, Any]:
    """
    Retrieves information about connected displays.

    Returns:
        A dictionary containing the number of monitors and details for each monitor.
    """
    return operations.get_screen_info()


@mcp_server.tool()
async def capture_screen_by_number(monitor_number: int) -> Dict[str, Any]:
    """
    Captures a screenshot of the specified monitor.

    Args:
        monitor_number: The number of the monitor to capture.

    Returns:
        A dictionary containing the base64-encoded image and its mime type.
    """
    return operations.capture_screen_by_number(monitor_number)


@mcp_server.tool()
async def capture_all_screens() -> Dict[str, Any]:
    """
    Captures all connected monitors and stitches them into a single image.

    Returns:
        A dictionary containing the base64-encoded stitched image and its mime type.
    """
    return operations.capture_all_screens()


@mcp_server.tool()
async def get_window_list() -> List[Dict[str, Any]]:
    """
    Retrieves a list of currently open windows.

    Returns:
        A list of dictionaries, each containing details about a window (id, title, size, position).
    """
    return operations.get_window_list()


@mcp_server.tool()
async def capture_window(window_id: int) -> Dict[str, Any]:
    """
    Captures a screenshot of the specified window.

    Args:
        window_id: The ID of the window to capture.

    Returns:
        A dictionary containing the base64-encoded image and its mime type.
    """
    return operations.capture_window(window_id)


async def run_server():
    """Runs the MCP server over stdio."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=mcp_server.name,
                server_version=mcp_server.version,
                capabilities=mcp_server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main():
    """
    Checks for platform-specific dependencies and starts the server.
    """
    system = platform.system()
    missing_dependency = False
    if system == "Linux":
        try:
            from Xlib import display  # noqa: F401
        except ImportError:
            print("Error: python-xlib is not installed. Please run 'pip install \"mcp-screen-operation[linux]\"'")
            missing_dependency = True
    elif system == "Windows":
        try:
            import win32gui  # noqa: F401
        except ImportError:
            print("Error: pywin32 is not installed. Please run 'pip install \"mcp-screen-operation[windows]\"'")
            missing_dependency = True
    elif system == "Darwin":
        try:
            from Quartz import CGWindowListCopyWindowInfo  # noqa: F401
        except ImportError:
            print("Error: PyObjC is not installed. Please run 'pip install \"mcp-screen-operation[macos]\"'")
            missing_dependency = True

    if missing_dependency:
        return

    print(f"Starting {mcp_server.name} v{mcp_server.version}...")
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("Server stopped.")


if __name__ == "__main__":
    main()
