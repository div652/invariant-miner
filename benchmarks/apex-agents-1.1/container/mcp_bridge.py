"""Bridge DSH's stdio MCP connection to the world's MCP gateway, inside Mercor's 1.1 world container.

    podman exec -i <world> /app/.venv/bin/python /opt/dsh-bench/lib/mcp_bridge.py

A FastMCP proxy (the world's own gateway is one too; fastmcp is in the world image's /app/.venv) from stdio to
http://127.0.0.1:8000/mcp: tools, their schemas and results pass through unchanged. DSH reaches the gateway without
the world having a network (podman exec, not a published port). Mercor's agent reaches the same gateway over HTTP
from its own container (http://world:8000/mcp).
"""

from fastmcp import FastMCP

FastMCP.as_proxy("http://127.0.0.1:8000/mcp", name="world").run(transport="stdio", show_banner=False)
