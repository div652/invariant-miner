Scripts behind ../RETRIEVAL.md (2026-11-13). Run from this folder with python3:
extract.py (all tool calls of the 96 trajectories -> /tmp/retr/data.pkl), gold.py (gold matters per task from the
rubric), classify.py (search method per call), attrib.py (per gold matter: surfaced / opened / included -> rows.pkl).
The tables were computed with short ad-hoc queries over rows.pkl and data.pkl, and a re-run of capped and
case-sensitive globs against work/harvey-labs/tasks/firm-knowledge/dms. Paths assume ~/dsh-bench-harness.
