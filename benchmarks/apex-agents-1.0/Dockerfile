# APEX-Agents task image: Archipelago's environment image plus what its open-source build leaves out.
#
#   podman build -t dsh-bench-apex-agents:f8e41cb --build-arg BASE=dsh-bench-apex-agents-env:f8e41cb benchmarks/apex-agents-1.0
#
# BASE is Archipelago's environment/Dockerfile at the pinned commit, built unmodified by benchmarks/apex-agents-1.0/setup.sh.
# This layer (CHECKLIST.md, "Changes from Archipelago's own setup", change 2):
#   - code_exec's package mirror /usr/local/lib/code_execution, which code_exec's sandbox puts on PYTHONPATH (Python
#     packages), NODE_PATH (node_modules) and first on PATH (bin/, the soffice wrapper LibreOffice needs under the
#     sandbox shim). Mercor's images fill it with an internal install task that is not in the open-source repo; the
#     open-source Dockerfile's fallback (pip into the system Python) fails with ResolutionImpossible and the failure is
#     hidden by `;`. Here: the exact versions of code_exec's uv.lock (--no-deps: no re-resolution), its
#     node_tools/package-lock.json, and its sandbox_bin/soffice.
#   - ripgrep, for DSH's glob/grep (they run in this container).
# Helper scripts (benchmarks/apex-agents-1.0/container/) are mounted read-only at run time, not baked in.
ARG BASE=dsh-bench-apex-agents-env:f8e41cb
FROM ${BASE}

ARG MIRROR=/usr/local/lib/code_execution
ARG CODE=/app/mcp_servers/code

RUN set -eu; \
    cd "${CODE}"; \
    uv export --frozen --no-dev --no-hashes --no-header > /tmp/code-exec-all.txt; \
    grep -v -e '^-e ' -e '^mercor-rls-code-execution' -e '^Resolved ' -e '^pip=' -e '^ *#' -e '^ *$' \
      /tmp/code-exec-all.txt > /tmp/code-exec-requirements.txt; \
    /usr/bin/python3 -m pip install --break-system-packages --no-cache-dir --no-deps --quiet \
      --target "${MIRROR}" -r /tmp/code-exec-requirements.txt; \
    rm -f /tmp/code-exec-all.txt /tmp/code-exec-requirements.txt; \
    cp -r "${CODE}/node_tools" /tmp/node_tools; \
    cd /tmp/node_tools; \
    npm ci --omit=dev --no-audit --no-fund --loglevel=error; \
    mv node_modules "${MIRROR}/node_modules"; \
    cd /; rm -rf /tmp/node_tools; \
    mkdir -p "${MIRROR}/bin"; \
    install -m 0755 "${CODE}/mcp_servers/code_execution_server/sandbox_bin/soffice" "${MIRROR}/bin/soffice"; \
    chmod -R a+rX "${MIRROR}"

RUN apt-get update \
 && apt-get install -y --no-install-recommends ripgrep \
 && rm -rf /var/lib/apt/lists/*
