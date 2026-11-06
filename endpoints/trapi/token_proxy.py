"""TRAPI endpoint: a local proxy that authenticates DSH with the shared local token and TRAPI with a fresh Entra ID
token (az CLI, the SC-ALT account), then streams TRAPI's response back unchanged.

    endpoints/trapi/start.sh          (runs this in tmux `dsh-trapi`)

Why a proxy: DSH sends a fixed API key, TRAPI tokens live ~1.5 h and must be refreshed (trapi-model-access skill).
The Entra token is fetched with `az account get-access-token --scope api://trapi/.default` under
AZURE_CONFIG_DIR (default ~/.azure-scalt, the account with TRAPI access) and reused until 5 minutes before expiry.
It is never printed or logged. TRAPI_BASE_URL (the instance's .../openai/v1 URL) comes from the environment or
~/.config/dsh-bench/trapi.env; it is not stored in this repository.
"""

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from proxy_base import Upstream, serve  # noqa: E402


class EntraToken:
    def __init__(self, config_dir: str):
        self.env = os.environ | {"AZURE_CONFIG_DIR": os.path.expanduser(config_dir)}
        self.lock, self.value, self.expires = threading.Lock(), None, 0.0

    def get(self) -> str:
        with self.lock:
            if self.value is None or time.time() > self.expires - 300:
                out = subprocess.run(["az", "account", "get-access-token", "--scope", "api://trapi/.default", "-o", "json"],
                                     env=self.env, capture_output=True, text=True, timeout=120)
                if out.returncode != 0:
                    raise RuntimeError("az account get-access-token failed (log in again under AZURE_CONFIG_DIR)")
                data = json.loads(out.stdout)
                self.value, self.expires = data["accessToken"], float(data.get("expires_on") or time.time() + 3000)
            return self.value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.environ.get("DSH_BENCH_TRAPI_PORT", 8031)))
    parser.add_argument("--base-url", default=os.environ.get("TRAPI_BASE_URL"))
    parser.add_argument("--azure-config-dir", default=os.environ.get("AZURE_CONFIG_DIR", "~/.azure-scalt"))
    parser.add_argument("--log-bodies", type=Path)
    args = parser.parse_args()
    if not args.base_url:
        raise SystemExit("set TRAPI_BASE_URL (e.g. in ~/.config/dsh-bench/trapi.env)")
    token = EntraToken(args.azure_config_dir)
    token.get()  # fail at start, not on the first agent request

    def prepare(method, path, headers, body):
        headers["Authorization"] = "Bearer " + token.get()
        return headers, body

    serve(args.port, Upstream(args.base_url), prepare, log_bodies=args.log_bodies, name="trapi")


if __name__ == "__main__":
    main()
