# MCP Screen Operation Server

This project provides a Model Context Protocol (MCP) server for interacting with the user's screen and windows.

It exposes several tools that allow an MCP client to:
- Get information about connected displays.
- Capture screenshots of a specific monitor.
- Capture a stitched screenshot of all monitors.
- Get a list of open windows.
- Capture a screenshot of a specific window.

## Installation

It is recommended to install the project in a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode with the dependencies for your specific operating system.

### For Linux
```bash
pip install -e ".[linux]"
```

### For Windows
```bash
pip install -e ".[windows]"
```

### For macOS
```bash
pip install -e ".[macos]"
```

## Usage

Once installed, you can run the server using the following command:

```bash
screen-operation-server
```

The server will start and listen for connections over stdio.

## Tools

Here is a list of the available tools:

- `get_screen_info()`: Retrieves information about connected displays.
- `capture_screen_by_number(monitor_number: int)`: Captures a screenshot of the specified monitor.
- `capture_all_screens()`: Captures all connected monitors and stitches them into a single image.
- `get_window_list()`: Retrieves a list of currently open windows.
- `capture_window(window_id: int)`: Captures a screenshot of the specified window.
