# Contributing

Thanks for considering a contribution!

## Getting Started
- Python 3.11+
- `pip install pandas`
- Run `python src/start_json.py --config config/config.json` to generate outputs in `output/`.

## Code Layout
- `src/core/er_qc.py` — pure functions (feature engineering, scoring, decisions, QC, exports)
- `src/start_json.py` — CLI entrypoint; reads `config/config.json`
- `config/config.json` — **the only place** holding runtime variables (paths, weights, thresholds)
- `tests/smoke_test.py` — minimal test (no external frameworks)

## Submitting Changes
1. Fork → branch → changes.
2. Ensure `python tests/smoke_test.py` passes.
3. Open MR with a brief description (what/why).