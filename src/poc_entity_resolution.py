#!/usr/bin/env python3
"""src/poc_entity_resolution.py
Thin wrapper identical in spirit to the top-level `poc_entity_resolution.py`.
It exists so that tools expecting an entrypoint under `src/` can still run the POC.
All variables are read from `config/config.json` (no hard-coded values).
"""
from __future__ import annotations
import os, json
from core.er_qc import run_pipeline, summarize  # note: import path differs inside src/

def load_config(config_path: str) -> dict:
    """Load JSON configuration (relative to repo root)."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main() -> None:
    # Compute repo root as parent of this file's directory
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg_path = os.path.join(repo_root, "config", "config.json")
    cfg = load_config(cfg_path)

    input_csv  = cfg["paths"]["input"]
    output_dir = cfg["paths"]["output"]
    weights    = cfg["weights"]
    thresholds = cfg["thresholds"]
    top = run_pipeline(input_csv, output_dir, weights, thresholds)

    summary = summarize(top)
    report_lines = [
        f"Total rows: {summary['total_rows']}",
        f"Matched: {summary['decision_counts'].get('Matched', 0)}",
        f"Needs Review: {summary['decision_counts'].get('Needs Review', 0)}",
        f"Unmatched: {summary['decision_counts'].get('Unmatched', 0)}",
        f"Clean rows: {summary['clean_rows']}",
        f"Rows with flags: {summary['has_flags_rows']}",
    ]
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "run_report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(report_lines) + "\n")

if __name__ == "__main__":
    main()