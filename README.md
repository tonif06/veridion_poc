# veridion_poc — Procurement POC (CSV-only, JSON config)

This repository contains a small prototype (POC) for supplier entity resolution and data quality checks.

- **Backend**: Python (pandas, stdlib only).
- **Frontend**: Power BI (using the CSV outputs and provided DAX measures).

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