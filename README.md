

# veridion_poc — Procurement POC (CSV-only, JSON config)

This repository contains a small prototype (POC) for supplier entity resolution and data quality checks.

- **Backend**: Python (pandas, stdlib only).
- **Frontend**: Power BI (using the CSV outputs and provided DAX measures). - https://download.microsoft.com/download/8/8/0/880bca75-79dd-466a-927d-1abf1f5454b0/PBIDesktopSetup_x64.exe

## Run locally
```bash
python src/start_json.py --config config/config.json
```

## Configuration
All variables (file paths, weights, thresholds) are stored in `config/config.json`.  
No values are hard-coded in the code.

You can override them on the command line, e.g.:
```bash
python src/start_json.py --config config/config.json --input data/myfile.csv --output out --strong 0.8
```

## Outputs
The pipeline writes CSV files into the `output/` folder:
- `matches_decisions.csv` — full results
- `matched_only.csv` — only high-confidence matches
- `needs_review.csv` — borderline cases
- `unmatched.csv` — unresolved rows
- `qc_summary.csv` — clean vs flagged summary
- `run_report.txt` — quick human-readable summary

## Power BI
Load `output/matches_decisions.csv` and `output/qc_summary.csv`.  
Add measures from `powerbi/measures/Measures.md`.

## GitHub — How to create and push the repo
1. Create a new repository on GitHub (empty, no README).
2. In your local folder:
```bash
git init
git add .
git commit -m "Initial commit: JSON-config POC"
git branch -M main
git remote add origin https://github.com/<your-username>/veridion_poc.git
git push -u origin main
```

3. (Optional) Add a GitHub Actions workflow for CI (instead of GitLab CI).
## Documentation

- [Presentation overview](PRESENTATION.md): explains what the project does, the algorithms used, and how it works.


# Entity Resolution & Data Quality POC
*A Python + Power BI Prototype*

---

## Project Goal
- Help a **Procurement department** clean and unify supplier data.  
- Enable category managers to:  
  - Identify duplicate or messy records.  
  - See a clear picture of spend by supplier.  
- Provide leadership with:  
  - Reliable cost-saving insights.  
  - A foundation for **sustainability analytics** in the future.  

---

## Core Idea
**Entity Resolution (ER):**  
Link multiple records that represent the same real-world company.  

**Data Quality Checks (QC):**  
Flag missing, outdated, or inconsistent information.  

**Result:**  
- **Matched suppliers** → ready to use.  
- **Needs Review** → borderline cases.  
- **Unmatched** → no reliable candidate found.  

---

## Technology Stack
- **Backend:** Python (pandas, NumPy, standard library)  
- **Frontend:** Power BI (visualization & DAX measures)  
- **Configuration:** JSON (no hard-coded variables)  
- **Version control & CI/CD:** GitHub repo + optional GitHub Actions  

---

## Libraries Used
- **pandas** → data manipulation, CSV I/O  
- **NumPy** → numerical operations  
- **difflib.SequenceMatcher** (Python stdlib) → string similarity for company names  
- **datetime** (Python stdlib) → freshness scoring  
- **os/json/argparse** (Python stdlib) → file handling, configuration, CLI interface  

---

## Algorithms

### 1. String Similarity (Name Matching)
- `SequenceMatcher` computes ratio between input name and candidate name (0–1).  

### 2. Feature Engineering
- **Country match** → binary (1 if equal)  
- **City match** → binary (1 if equal)  
- **Website presence** → binary (1 if website exists)  
- **Freshness** → score based on last update date (recent = higher)  

### 3. Weighted Match Score
```
score = 0.6 * name_similarity
      + 0.15 * country_match
      + 0.10 * city_match
      + 0.10 * freshness
      + 0.05 * has_website
```

### 4. Decision Rules
- If name similarity < 0.70 → **Unmatched**  
- If score ≥ 0.75 → **Matched**  
- If 0.60 ≤ score < 0.75 → **Needs Review**  
- Else → **Unmatched**  

### 5. Quality Flags
- Missing postcode/street  
- No website or social presence  
- Stale update (>2 years)  
- Missing company type  

---

## Outputs
- `matches_decisions.csv` → full resolved dataset  
- `matched_only.csv` → clean subset for immediate use  
- `needs_review.csv` → review queue for ops team  
- `unmatched.csv` → unresolved records  
- `qc_summary.csv` → clean vs flagged summary  
- `run_report.txt` → human-readable overview  

---

## Visualization in Power BI
- **Executive Summary:** KPI cards (Matched, Needs Review, Unmatched), donut chart, stacked bar (Clean vs Has Flags)  
- **Data Quality:** Distribution of QC flags, freshness trends  
- **Review Queue:** Table with input name, candidate, match score, QC flags, links  
- **(Optional) Sustainability:** Treemap by sector, to show ESG potential once data is clean  

---

## Why It Matters
- Reduces noise in supplier master data  
- Builds trust in analytics dashboards  
- Saves time for procurement managers  
- Lays the groundwork for sustainability and compliance reporting  

---

## Next Steps
- Enhance algorithms with ML-based similarity (e.g., embeddings, fuzzy matching)  
- Connect directly to ERP / Procurement systems  
- Scale to millions of records with Spark/Dask  
- Add sustainability datasets (e.g., CO₂ footprint, ESG ratings
