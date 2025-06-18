import argparse
from typing import Any, Dict, List

from fastmcp import FastMCP

from . import operations
from .window_manager import WindowManagerFactory

# FastMCPインスタンスを作成
mcp = FastMCP("screen-operation-server")


@mcp.tool()
async def get_screen_info() -> Dict[str, Any]:
    """
    Retrieves information about connected displays.

    Returns:
        A dictionary containing the number of monitors and details for each monitor.
    """
    return operations.get_screen_info()


@mcp.tool()
async def capture_screen_by_number(monitor_number: int) -> Dict[str, Any]:
    """
    Captures a screenshot of the specified monitor.

    Args:
        monitor_number: The number of the monitor to capture.

    Returns:
        A dictionary containing the base64-encoded image and its mime type.
    """
    return operations.capture_screen_by_number(monitor_number)


@mcp.tool()
async def capture_all_screens() -> Dict[str, Any]:
    """
    Captures all connected monitors and stitches them into a single image.

    Returns:
        A dictionary containing the base64-encoded stitched image and its mime type.
    """
    return operations.capture_all_screens()


@mcp.tool()
async def get_window_list() -> List[Dict[str, Any]]:
    """
    Retrieves a list of currently open windows.

    Returns:
        A list of dictionaries, each containing details about a window (id, title, size, position).
    """
    return operations.get_window_list()


@mcp.tool()
async def capture_window(window_id: int) -> Dict[str, Any]:
    """
    Captures a screenshot of the specified window.

    Args:
        window_id: The ID of the window to capture.

    Returns:
        A dictionary containing the base64-encoded image and its mime type.
    """
    return operations.capture_window(window_id)


def main():
    """
    Main entry point that supports multiple transport protocols.
    """
    # プラットフォーム依存関係をチェック
    WindowManagerFactory.check_platform_dependencies()

    # コマンドライン引数を解析
    parser = argparse.ArgumentParser(description="MCP Screen Operation Server")
    parser.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default="stdio", help="Transport protocol to use (default: stdio)")
    parser.add_argument("--port", type=int, default=8080, help="Port for HTTP-based transports (default: 8080)")
    parser.add_argument("--host", default="127.0.0.1", help="Host for HTTP-based transports (default: 127.0.0.1)")

    args = parser.parse_args()

    print(f"Starting {mcp.name} v0.1.0 with {args.transport} transport...")

    try:
        if args.transport == "stdio":
            # STDIOトランスポート（デフォルト）
            mcp.run(transport="stdio")
        elif args.transport == "sse":
            # SSEトランスポート
            print(f"SSE endpoint: http://{args.host}:{args.port}/sse")
            mcp.run(transport="sse", host=args.host, port=args.port)
        elif args.transport == "streamable-http":
            # Streamable HTTPトランスポート（推奨）
            print(f"Streamable HTTP endpoint: http://{args.host}:{args.port}/mcp")
            mcp.run(transport="streamable-http", host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("Server stopped.")


if __name__ == "__main__":
    main()
