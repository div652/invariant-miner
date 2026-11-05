# Minimal default sandbox image: where bash and glob/grep run when a benchmark brings no image of its own.
# The agent loop (node, DSH) runs on the host, so node is NOT installed here.
# Harness requirements in ANY image: bash, coreutils `timeout`, ripgrep (`rg`).
# Benchmark needs go in benchmarks/<name>/Dockerfile (FROM dsh-bench-base), never here.

FROM docker.io/library/python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends ripgrep procps \
    && rm -rf /var/lib/apt/lists/*

CMD ["sleep", "infinity"]
