#!/usr/bin/env python3
"""start_json.py
CLI entrypoint that reads `config/config.json` and starts the ER + QC pipeline.

Why this file exists when we also have `poc_entity_resolution.py`?
- `poc_entity_resolution.py` is a minimal launcher for non-technical users.
- `start_json.py` adds a **command-line interface (CLI)** so you can override config values without editing JSON.

Usage examples:
    python src/start_json.py --config config/config.json
    python src/start_json.py --config config/config.json --input data/other.csv --output out --strong 0.8
"""
from __future__ import annotations

import os
import json
import argparse
from core.er_qc import run_pipeline, summarize

def parse_args() -> argparse.Namespace:
    """Define and parse command-line arguments for the CLI."""
    p = argparse.ArgumentParser(description="Start pipeline with JSON config (no vars hard-coded)")
    p.add_argument("--config", default="config/config.json", help="Path to JSON config file")
    p.add_argument("--input", help="Override input CSV path")
    p.add_argument("--output", help="Override output folder")
    p.add_argument("--strong", type=float, help="Override 'strong' threshold (Matched cutoff)")
    p.add_argument("--review", type=float, help="Override 'review' threshold (Needs Review cutoff)")
    p.add_argument("--name_floor", type=float, help="Override minimum name similarity hard floor")
    return p.parse_args()

def load_config(path: str) -> dict:
    """Load JSON configuration from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)

    # Extract values from JSON
    input_csv  = cfg["paths"]["input"]
    output_dir = cfg["paths"]["output"]
    weights    = cfg["weights"]
    thresholds = cfg["thresholds"]

    # Apply CLI overrides when provided
    if args.input: input_csv = args.input
    if args.output: output_dir = args.output
    if args.strong is not None: thresholds["strong"] = args.strong
    if args.review is not None: thresholds["review"] = args.review
    if args.name_floor is not None: thresholds["name_hard_floor"] = args.name_floor

    # Run pipeline and summarize
    top = run_pipeline(input_csv, output_dir, weights, thresholds)
    s = summarize(top)

    report_lines = [
        f"Total rows: {s['total_rows']}",
        f"Matched: {s['decision_counts'].get('Matched', 0)}",
        f"Needs Review: {s['decision_counts'].get('Needs Review', 0)}",
        f"Unmatched: {s['decision_counts'].get('Unmatched', 0)}",
        f"Clean rows: {s['clean_rows']}",
        f"Rows with flags: {s['has_flags_rows']}",
    ]
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "run_report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(report_lines) + "\n")
    print("[OK] Pipeline finished. Outputs in:", output_dir)

if __name__ == "__main__":
    main()