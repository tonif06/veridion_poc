#!/usr/bin/env python3
"""poc_entity_resolution.py
Beginner-friendly launcher for the Entity Resolution (ER) + Quality Check (QC) pipeline.

This script is intentionally simple — it orchestrates the flow:
  1) Read configuration from `config/config.json` (no hard-coded values).
  2) Extract variables (paths, weights, thresholds).
  3) Run the ER + QC pipeline defined in `src/core/er_qc.py`.
  4) Write a tiny human-readable summary into `output/run_report.txt`.
  5) Print the summary to the console.

Run from the repository root:
    python poc_entity_resolution.py
"""

from __future__ import annotations

# --- Standard library imports ---
import os   # file system utilities: join paths, create folders
import json # read the JSON configuration file

# --- Project imports (our own modules) ---
# run_pipeline: executes the full ER + QC process end-to-end
# summarize:    builds a small, human-readable summary dictionary
from src.core.er_qc import run_pipeline, summarize


def load_config(config_path: str) -> dict:
    """Load and parse the JSON configuration file.

    Parameters
    ----------
    config_path : str
        Path to the JSON file (e.g., 'config/config.json').

    Returns
    -------
    dict
        A dictionary with keys:
        - 'paths'      : {'input': <csv path>, 'output': <dir>}
        - 'weights'    : feature weights used for the match score
        - 'thresholds' : decision thresholds for Matched / Needs Review / Unmatched
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    """Main entrypoint: read config, run pipeline, save and print summary."""
    # (1) Compute repository root (folder that contains this file).
    repo_root = os.path.dirname(os.path.abspath(__file__))

    # (2) Build the path to the JSON config (kept next to `src/` in `config/`).
    config_path = os.path.join(repo_root, "config", "config.json")  # change only if you move the JSON

    # (3) Load configuration from JSON (NO hard-coded values in code).
    cfg = load_config(config_path)

    # (4) Extract variables from config.
    input_csv  = cfg["paths"]["input"]    # e.g., 'data/presales_data_sample.csv'
    output_dir = cfg["paths"]["output"]   # e.g., 'output'
    weights    = cfg["weights"]             # model weights for scoring
    thresholds = cfg["thresholds"]          # decision thresholds

    # (5) Run the full ER + QC pipeline:
    #     - Reads the input CSV
    #     - Engineers features (similarity, freshness, etc.)
    #     - Computes a match score using the given weights
    #     - Chooses the best candidate per input row
    #     - Labels rows as Matched / Needs Review / Unmatched
    #     - Exports multiple CSV files into the output directory
    top = run_pipeline(input_csv, output_dir, weights, thresholds)

    # (6) Summarize results into a human-readable dictionary.
    summary = summarize(top)

    # (7) Prepare lines for a tiny text report.
    report_lines = [
        f"Total rows: {summary['total_rows']}",
        f"Matched: {summary['decision_counts'].get('Matched', 0)}",
        f"Needs Review: {summary['decision_counts'].get('Needs Review', 0)}",
        f"Unmatched: {summary['decision_counts'].get('Unmatched', 0)}",
        f"Clean rows: {summary['clean_rows']}",
        f"Rows with flags: {summary['has_flags_rows']}",
    ]

    # (8) Ensure the output directory exists.
    os.makedirs(output_dir, exist_ok=True)

    # (9) Write the report to disk.
    report_path = os.path.join(output_dir, "run_report.txt")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(report_lines) + "\n")  # newline at end for POSIX compatibility

    # (10) Print the same summary for convenience.
    print("[OK] POC finished. Outputs written to:", output_dir)
    print("      Summary:")
    for line in report_lines:
        print("      ", line)


if __name__ == "__main__":
    main()