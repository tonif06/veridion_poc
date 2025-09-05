# Power BI — Procurement POC Frontend

This guide builds a compact report over the `output/*.csv` files from the Python backend.

## Data
- Load `matches_decisions.csv` and `qc_summary.csv`.
- Rename tables to **Matches** and **QC_Summary**.

## Measures (DAX)
Create in **Matches**:
```
Matched Rows := COUNTROWS(FILTER(Matches, Matches[decision] = "Matched"))
Needs Review Rows := COUNTROWS(FILTER(Matches, Matches[decision] = "Needs Review"))
Unmatched Rows := COUNTROWS(FILTER(Matches, Matches[decision] = "Unmatched"))
Clean Rows := COUNTROWS(FILTER(Matches, Matches[qc_flags] = ""))
```

## Visuals
1. **KPI Cards**: `Matched Rows`, `Needs Review Rows`, `Unmatched Rows`.
2. **Bar chart**: Count of rows by `decision` (from Matches).
3. **Bar chart**: `rows` by `decision` from **QC_Summary** (optional compare).
4. **Table (Review Queue)**: `input_company_name`, `company_name`, `match_score`, `decision`, `decision_notes`, `qc_flags`.
5. **Slicers**: `decision`, and a derived column for QC cleanliness:

Add a calculated column in Matches:
```
QC_Status = IF(Matches[qc_flags] = "", "clean", "has_flags")
```

## Drill-through (optional)
- Create a drill-through page on `input_row_key` to show the chosen match details.
- Include external links as columns: `website_url`, `linkedin_url` for quick validation.

## Narrative Page (client-facing)
- Summarize the method and thresholds:
  - Matching score weights (Name 60%, Country 15%, City 10%, Freshness 10%, Website 5%)
  - Thresholds: Matched ≥ 0.75, Needs Review in [0.60, 0.75), Unmatched otherwise; name_sim floor 0.70
- Include a short blurb on QC policy and next steps for unresolved items.