"""Start Archipelago's app servers once, over HTTP, inside the environment container; print the gateway config.

    python3 start_apps.py servers.json > gateway.json

servers.json: {"servers": {name: {"cwd", "command", "args", "env", "port"}}, "secret_files": {name: {ENV: path}}}.
Each server runs with the example config's command and environment plus MCP_TRANSPORT=http and MCP_PORT (each
server's own HTTP mode); see CHECKLIST.md, "Changes from Archipelago's own setup" (1). A server's secrets are read from
files (e.g. the FMP key, written by the host just before) into that server's environment only, then the files are
deleted. The printed config points Archipelago's gateway (POST /apps) at the running servers.
"""

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

LOGS = Path("/tmp/apps")


def wait_listening(port: int, deadline: float) -> bool:
    while time.monotonic() < deadline:
        with socket.socket() as s:
            s.settimeout(1)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.25)
    return False


def main() -> int:
    spec = json.loads(Path(sys.argv[1]).read_text())
    LOGS.mkdir(exist_ok=True)
    for name, server in spec["servers"].items():
        env = os.environ | server.get("env", {}) | {"MCP_TRANSPORT": "http", "MCP_PORT": str(server["port"])}
        for var, path in spec.get("secret_files", {}).get(name, {}).items():
            env[var] = Path(path).read_text().strip()
            Path(path).unlink()
        with (LOGS / f"{name}.log").open("wb") as log:
            subprocess.Popen([server["command"], *server["args"]], cwd=server["cwd"], env=env, stdout=log,
                             stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
    deadline = time.monotonic() + float(spec.get("timeout_s", 180))
    down = [name for name, server in spec["servers"].items() if not wait_listening(server["port"], deadline)]
    if down:
        print(f"servers not listening: {down}", file=sys.stderr)
        return 1
    print(json.dumps({"mcpServers": {name: {"transport": "http", "url": f"http://127.0.0.1:{server['port']}/mcp"}
                                     for name, server in spec["servers"].items()}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
