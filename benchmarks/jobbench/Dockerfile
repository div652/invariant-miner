# JobBench sandbox image: what the reference runs' agents had for bash.
# Reference (agentic-evolution, run_benchmark_dsh_nobwrap.sh): the JobBench venv's python (Python 3.12, the packages of
# job-bench-eval's uv.lock -> requirements.txt, exported with `uv export --locked --no-dev`), plus the host's CLIs:
# LibreOffice (soffice), poppler (pdftotext/pdftoppm), pandoc, sqlite3, git, curl, wget.
FROM dsh-bench-base

RUN apt-get update && apt-get install -y --no-install-recommends \
        libreoffice-core libreoffice-writer libreoffice-calc libreoffice-impress \
        poppler-utils pandoc sqlite3 git curl wget ca-certificates fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
