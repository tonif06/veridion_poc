# tests/smoke_test.py
# A tiny, framework-free smoke test you can run with:  python tests/smoke_test.py
# It checks that: (1) we can process a small sample, and (2) expected CSV outputs are created.

from __future__ import annotations

import os
import sys
import json
import pandas as pd

# Allow `import core.er_qc` when running this file directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from core.er_qc import run_pipeline

CFG = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')

def main() -> None:
    # (1) Read config JSON
    with open(CFG, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # (2) Pull values
    input_csv = cfg['paths']['input']
    output_dir = 'output_test'  # use a separate folder so we don't mix with production outputs
    weights = cfg['weights']
    thresholds = cfg['thresholds']

    # (3) Read a small sample for faster test runs (first 200 rows)
    df = pd.read_csv(input_csv).head(200)
    tmp = os.path.join('/tmp', 'poc_smoke.csv')
    df.to_csv(tmp, index=False)

    # (4) Run the pipeline and check that it produced outputs
    top = run_pipeline(tmp, output_dir, weights, thresholds)
    assert len(top) > 0, 'No rows processed — something is wrong with the pipeline.'

    # (5) Verify that key CSVs exist
    for fn in ['matches_decisions.csv','matched_only.csv','needs_review.csv','unmatched.csv','qc_summary.csv']:
        path = os.path.join(output_dir, fn)
        assert os.path.exists(path), f'Missing expected output file: {fn}'

    print('[SMOKE] OK — outputs generated in', output_dir)

if __name__ == '__main__':
    main()