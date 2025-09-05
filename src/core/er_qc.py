# src/core/er_qc.py
# Core logic for Entity Resolution (ER) and Quality Checks (QC).
# - Pure functions: no hard-coded paths or thresholds.
# - Designed to be easy-to-read for beginners.

from __future__ import annotations

import os
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any, Dict

def norm(s: Any) -> str:
    """Normalize a value to a comparable lowercase string.
    - Convert NaN to empty string
    - Strip whitespace
    - Lowercase

    This makes string comparisons more reliable.
    """
    if pd.isna(s):
        return ""
    return str(s).strip().lower()

def sim(a: Any, b: Any) -> float:
    """Compute similarity between two strings using SequenceMatcher.
    Returns a ratio in [0, 1], where 1 means identical.
    """
    return SequenceMatcher(None, norm(a), norm(b)).ratio()

def parse_dt(s: Any):
    """Parse an ISO8601-like string into a datetime, if possible.
    Returns None if parsing fails or input is empty.
    """
    if pd.isna(s) or s == "":
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z","+00:00"))
    except Exception:
        return None

def freshness_score(days: Any) -> float:
    """Map 'days since last update' into a score (higher = fresher).
    The bins are simple and can be tuned later.
    """
    if pd.isna(days):
        return 0.3
    if days <= 365:
        return 1.0
    if days <= 730:
        return 0.7
    if days <= 1095:
        return 0.5
    return 0.3

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add columns (features) used by the matcher and QC logic.
    Assumes the DataFrame contains the following columns:
      - input_company_name, company_name
      - input_main_country_code, main_country_code
      - input_main_city, main_city
      - website_url, last_updated_at
    """
    today = datetime.now(timezone.utc)
    df = df.copy()
    df["name_similarity"] = df.apply(lambda r: sim(r.get("input_company_name",""), r.get("company_name","")), axis=1)
    df["country_match"] = (df.get("input_main_country_code","") == df.get("main_country_code","")).astype(int)
    df["city_match"] = df.apply(
        lambda r: int(norm(r.get("input_main_city","")) != "" and norm(r.get("input_main_city","")) == norm(r.get("main_city",""))),
        axis=1
    )
    df["has_website"] = (~df["website_url"].isna() & (df["website_url"].astype(str).str.len() > 0)).astype(int)
    last_upd = df["last_updated_at"].apply(parse_dt)
    df["days_since_update"] = last_upd.apply(lambda d: (today - d).days if isinstance(d, datetime) else np.nan)
    df["freshness"] = df["days_since_update"].apply(freshness_score)
    return df

def score_candidates(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    """Combine features into a single weighted 'match_score'."""
    df = df.copy()
    df["match_score"] = (
        weights.get("name_similarity",0.6)*df["name_similarity"]
        + weights.get("country_match",0.15)*df["country_match"]
        + weights.get("city_match",0.1)*df["city_match"]
        + weights.get("freshness",0.1)*df["freshness"]
        + weights.get("has_website",0.05)*df["has_website"]
    )
    return df

def decide(top_row: pd.Series, thresholds: Dict[str, float]) -> str:
    """Label a row as 'Matched', 'Needs Review', or 'Unmatched' based on thresholds."""
    name_floor = thresholds.get("name_hard_floor", 0.70)
    strong = thresholds.get("strong", 0.75)
    review = thresholds.get("review", 0.60)
    if top_row["name_similarity"] < name_floor:
        return "Unmatched"
    if top_row["match_score"] >= strong:
        return "Matched"
    if top_row["match_score"] >= review:
        return "Needs Review"
    return "Unmatched"

def decision_notes(r: pd.Series) -> str:
    """Produce a short audit trail for the decision (for explainability)."""
    bits = [f"name_sim={r['name_similarity']:.2f}"]
    bits.append("country✓" if r["country_match"]==1 else "country✗")
    if r["city_match"]==1: bits.append("city✓")
    if r["has_website"]==1: bits.append("website✓")
    bits.append(f"fresh={r['freshness']:.2f}")
    bits.append(f"score={r['match_score']:.2f}")
    return "; ".join(bits)

def qc_flags_row(r: pd.Series) -> str:
    """Generate data quality flags (missing fields, staleness, no web presence)."""
    flags = []
    if pd.isna(r.get("main_postcode")) or str(r.get("main_postcode")).strip() == "":
        flags.append("missing_postcode")
    if pd.isna(r.get("main_street")) or str(r.get("main_street")).strip() == "":
        flags.append("missing_street")
    socials = ["linkedin_url","facebook_url","twitter_url","youtube_url","instagram_url","tiktok_url"]
    has_social = any([(not pd.isna(r.get(s))) and str(r.get(s)).strip() != "" for s in socials])
    if r.get("has_website",0) == 0 and not has_social:
        flags.append("no_website_no_social")
    if not pd.isna(r.get("days_since_update")) and r.get("days_since_update") > 730:
        flags.append("stale_update_>2y")
    if pd.isna(r.get("company_type")) or str(r.get("company_type")).strip() == "":
        flags.append("missing_company_type")
    return ", ".join(flags) if flags else ""

def pick_top_and_label(df: pd.DataFrame, thresholds: Dict[str, float]) -> pd.DataFrame:
    """Within each input record, keep only the best candidate and label it."""
    df = df.copy()
    df["rank_in_group"] = df.groupby("input_row_key")["match_score"].rank(method="first", ascending=False)
    top = df[df["rank_in_group"] == 1].copy()
    top["decision"] = top.apply(lambda r: decide(r, thresholds), axis=1)
    top["decision_notes"] = top.apply(decision_notes, axis=1)
    top["qc_flags"] = top.apply(qc_flags_row, axis=1)
    return top

def export_outputs(top_df: pd.DataFrame, output_dir: str) -> None:
    """Write multiple CSVs for downstream consumption and reporting."""
    os.makedirs(output_dir, exist_ok=True)
    cols = [
        "input_row_key","input_company_name","input_main_country_code","input_main_city",
        "veridion_id","company_name","main_country_code","main_city","website_url",
        "name_similarity","country_match","city_match","freshness","has_website","match_score",
        "decision","decision_notes","qc_flags"
    ]
    matches = top_df[cols].sort_values(["decision","match_score"], ascending=[True, False]).reset_index(drop=True)
    matched = matches[matches["decision"]=="Matched"].copy()
    needs_review = matches[matches["decision"]=="Needs Review"].copy()
    unmatched = matches[matches["decision"]=="Unmatched"].copy()
    qc_summary = (
        matches.assign(flag=lambda d: d["qc_flags"].apply(lambda x: "clean" if x=="" else "has_flags"))
               .groupby(["decision","flag"], dropna=False).size().reset_index(name="rows")
    )
    matches.to_csv(os.path.join(output_dir, "matches_decisions.csv"), index=False)
    matched.to_csv(os.path.join(output_dir, "matched_only.csv"), index=False)
    needs_review.to_csv(os.path.join(output_dir, "needs_review.csv"), index=False)
    unmatched.to_csv(os.path.join(output_dir, "unmatched.csv"), index=False)
    qc_summary.to_csv(os.path.join(output_dir, "qc_summary.csv"), index=False)

def run_pipeline(input_csv: str, output_dir: str, weights: Dict[str, float], thresholds: Dict[str, float]):
    """End-to-end run: read -> engineer features -> score -> select -> label -> export."""
    df = pd.read_csv(input_csv)
    df = engineer_features(df)
    df = score_candidates(df, weights)
    top = pick_top_and_label(df, thresholds)
    export_outputs(top, output_dir)
    return top

def summarize(matches_df: pd.DataFrame) -> Dict[str, Any]:
    """Return a small dictionary summarizing the results for quick reporting."""
    d: Dict[str, Any] = {}
    total = len(matches_df)
    d["total_rows"] = total
    counts = matches_df["decision"].value_counts(dropna=False).to_dict()
    d["decision_counts"] = {k:int(v) for k,v in counts.items()}
    clean = matches_df["qc_flags"].fillna("").str.strip() == ""
    d["clean_rows"] = int(clean.sum())
    d["has_flags_rows"] = int((~clean).sum())
    return d