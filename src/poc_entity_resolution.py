#!/usr/bin/env python3
"""poc_entity_resolution.py
Hardened launcher for the Entity Resolution (ER) + Quality Check (QC) pipeline.

Adds:
- Robust config discovery + validation
- Path and schema checks before running the pipeline
- Logging (INFO by default, DEBUG if VERIDION_VERBOSE=1)
- Timing + pretty console summary
- Error file in output/error.log on failure

Recommended invocation (from repo root via run.py):
    python run.py
"""

from __future__ import annotations

import os
import sys
import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any, List, Tuple

from src.core.er_qc import run_pipeline, summarize


# ------------ Logging helpers ------------
def _is_verbose() -> bool:
    return os.environ.get("VERIDION_VERBOSE", "").strip() in {"1", "true", "True", "yes", "YES"}

def log_info(msg: str) -> None:
    print(f"[INFO] {msg}")

def log_debug(msg: str) -> None:
    if _is_verbose():
        print(f"[DEBUG] {msg}")

def log_warn(msg: str) -> None:
    print(f"[WARN] {msg}")

def log_error(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)


# ------------ Config discovery + validation ------------
def find_config() -> Path:
    """Find config/config.json via:
       1) VERIDION_CONFIG env var
       2) <repo_root>/config/config.json
       3) <cwd>/config/config.json
    """
    env_path = os.environ.get("VERIDION_CONFIG")
    if env_path:
        p = Path(env_path).expanduser()
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        if p.exists():
            log_debug(f"Using config from VERIDION_CONFIG: {p}")
            return p
        log_warn(f"VERIDION_CONFIG set but file not found: {p}")

    repo_root = Path(__file__).resolve().parent.parent
    candidate_repo = repo_root / "config" / "config.json"
    candidate_cwd = Path.cwd() / "config" / "config.json"

    for cand in (candidate_repo, candidate_cwd):
        if cand.exists():
            log_debug(f"Using config at: {cand}")
            return cand

    tried = "\n  - ".join(str(p) for p in (candidate_repo, candidate_cwd))
    raise FileNotFoundError(
        "Could not find config/config.json. Tried:\n  - " + tried +
        "\nYou can also set VERIDION_CONFIG to an explicit path."
    )


def load_config(config_path: Path) -> Dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg


def validate_config(cfg: Dict[str, Any]) -> None:
    """Validate presence and types of required config keys."""
    required_top = ["paths", "weights", "thresholds"]
    for k in required_top:
        if k not in cfg:
            raise KeyError(f"Missing `{k}` in config.json")

    # paths
    paths = cfg["paths"]
    for k in ["input", "output"]:
        if k not in paths or not isinstance(paths[k], str) or not paths[k]:
            raise KeyError(f"paths.{k} must be a non-empty string")

    # weights (floats)
    weights = cfg["weights"]
    if not isinstance(weights, dict) or not weights:
        raise KeyError("`weights` must be a non-empty object")

    # thresholds (floats)
    thresholds = cfg["thresholds"]
    for k in ["strong", "review", "name_hard_floor"]:
        if k not in thresholds:
            raise KeyError(f"Missing thresholds.{k}")
        try:
            float(thresholds[k])
        except Exception as e:
            raise TypeError(f"thresholds.{k} must be a number") from e


# ------------ Path + input checks ------------
def validate_paths(input_csv: str, output_dir: str) -> Tuple[Path, Path]:
    in_path = Path(input_csv)
    out_path = Path(output_dir)
    if not in_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {in_path}")
    # Make sure we can create output
    out_path.mkdir(parents=True, exist_ok=True)
    return in_path, out_path


def validate_input_schema(csv_path: Path, required_cols: List[str]) -> None:
    """Lightweight header validation to fail fast with a helpful error."""
    import csv
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, [])
    missing = [c for c in required_cols if c not in header]
    if missing:
        raise ValueError(
            "Input CSV is missing required columns:\n  - " + "\n  - ".join(missing) +
            "\nPlease export/prepare the CSV with the correct headers."
        )


# These are the columns used downstream by engineer_features in core/er_qc.py
REQUIRED_COLUMNS = [
    "input_row_key", "input_company_name", "input_main_country_code", "input_main_city",
    "company_name", "main_country_code", "main_city", "website_url", "last_updated_at",
    # optional but commonly present in outputs / QC:
    "main_postcode", "main_street", "company_type",
    # social columns referenced by QC flags (if missing, QC will just be less informative)
    "linkedin_url", "facebook_url", "twitter_url", "youtube_url", "instagram_url", "tiktok_url"
]


# ------------ Output helpers ------------
def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")

def write_error_log(out_dir: Path, exc: BaseException) -> None:
    err_path = out_dir / "error.log"
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    write_text(err_path, tb)
    log_error(f"Wrote error details to: {err_path}")


def render_summary_table(summary: Dict[str, Any]) -> str:
    """Pretty monospace table for terminal output."""
    def pct(part: int, total: int) -> str:
        return f"{(part / total * 100):6.2f}%" if total else "  0.00%"

    total = int(summary.get("total_rows", 0))
    dc = summary.get("decision_counts", {}) or {}
    matched = int(dc.get("Matched", 0))
    review  = int(dc.get("Needs Review", 0))
    unmatch = int(dc.get("Unmatched", 0))
    clean   = int(summary.get("clean_rows", 0))
    flagged = int(summary.get("has_flags_rows", 0))

    lines = []
    lines.append("+----------------------+----------+----------+")
    lines.append("| Metric               |   Count  |    Share |")
    lines.append("+----------------------+----------+----------+")
    lines.append(f"| Total Rows           | {total:8d} |  100.00% |")
    lines.append(f"| Matched              | {matched:8d} | {pct(matched, total):>8} |")
    lines.append(f"| Needs Review         | {review:8d} | {pct(review,  total):>8} |")
    lines.append(f"| Unmatched            | {unmatch:8d} | {pct(unmatch, total):>8} |")
    lines.append("+----------------------+----------+----------+")
    lines.append(f"| Clean                | {clean:8d} | {pct(clean, total):>8} |")
    lines.append(f"| Has Flags            | {flagged:8d} | {pct(flagged, total):>8} |")
    lines.append("+----------------------+----------+----------+")
    return "\n".join(lines)


# ------------ Main orchestration ------------
def main() -> None:
    start = time.time()
    try:
        config_path = find_config()
        log_info(f"Config: {config_path}")

        cfg = load_config(config_path)
        validate_config(cfg)

        input_csv  = cfg["paths"]["input"]
        output_dir = cfg["paths"]["output"]
        weights    = cfg["weights"]
        thresholds = cfg["thresholds"]

        in_path, out_path = validate_paths(input_csv, output_dir)
        log_info(f"Input CSV: {in_path}")
        log_info(f"Output dir: {out_path}")

        # Fast header check to fail early with clear message
        try:
            validate_input_schema(in_path, REQUIRED_COLUMNS)
        except Exception as e:
            log_warn(f"Schema check warning: {e}")
            log_warn("Continuing anyway; downstream may still succeed if features used are present.")

        log_info("Running pipeline…")
        log_debug(f"Weights: {weights}")
        log_debug(f"Thresholds: {thresholds}")

        top = run_pipeline(str(in_path), str(out_path), weights, thresholds)
        summary = summarize(top)

        # Human-readable summary file + pretty console table
        report_lines = [
            f"Total rows: {summary['total_rows']}",
            f"Matched: {summary['decision_counts'].get('Matched', 0)}",
            f"Needs Review: {summary['decision_counts'].get('Needs Review', 0)}",
            f"Unmatched: {summary['decision_counts'].get('Unmatched', 0)}",
            f"Clean rows: {summary['clean_rows']}",
            f"Rows with flags: {summary['has_flags_rows']}",
        ]
        (out_path / "run_report.txt").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

        elapsed = time.time() - start
        log_info(f"Done in {elapsed:0.2f}s. Outputs written to: {out_path}\n")
        print(render_summary_table(summary))

    except KeyboardInterrupt:
        log_error("Interrupted by user (Ctrl+C).")
        sys.exit(130)  # conventional exit code for SIGINT
    except Exception as e:
        # Try to write error log to output dir if we know it; otherwise, current dir.
        try:
            # best effort: if output dir was resolved already, use it; else use CWD
            out_dir = Path(cfg["paths"]["output"]) if "cfg" in locals() else Path.cwd()
            out_dir.mkdir(parents=True, exist_ok=True)
            write_error_log(out_dir, e)
        except Exception:
            # As a last resort, print full traceback
            traceback.print_exc()

        log_error(f"{type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
