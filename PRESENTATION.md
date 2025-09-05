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
- Add sustainability datasets (e.g., CO₂ footprint, ESG ratings)