# Changelog

## 0.3.0 — JSON-config & separate start script
- Removed variables from main code; moved to `config/config.json`.
- Added `src/start_json.py` as the entrypoint.
- Kept CSV outputs; Power BI flow unchanged.
- Added GitLab CI pipeline and basic smoke test.

## 0.2.x — Prior CSV-only refactor
- Entity Resolution + QC with CLI (INI-based), Power BI measures.

## 0.1.0 — Initial POC
- First pass of ER + QC + PBIX guidance.