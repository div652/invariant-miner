"""Bridge DSH's stdio MCP connection to Archipelago's gateway inside the environment container.

    podman exec -i <container> /app/.venv/bin/python /opt/dsh-bench-apex/mcp_bridge.py

A FastMCP proxy (Archipelago's own gateway is one too) from stdio to http://127.0.0.1:8080/mcp/: tools, their schemas
and results pass through unchanged. It lets DSH reach the gateway without the container having a network (podman exec,
not a published port).
"""

from fastmcp import FastMCP

FastMCP.as_proxy("http://127.0.0.1:8080/mcp/", name="apps").run(transport="stdio", show_banner=False)
