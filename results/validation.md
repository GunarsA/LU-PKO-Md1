# Verification record

- Python: 3.12.14 on Windows AMD64.
- All 8 unit tests passed (initial measured test runtime: 0.213 seconds).
- Independent equipment-order oracle agreed with exact search on two saved
  conflict cases and 12 seeded random tiny instances.
- All experiment schedules were independently checked during execution.
- Saved CSV audit passed: 160 rows, including 140 SA runs, 14 baselines,
  and 6 exact results; five seeds at each of two budgets per instance.
- CSV dimensions, baseline references, nonnegative runtimes, and gaps checked.
- Both saved sample priority lists reproduce their reported objective and makespan.
- SA matched the proven optimum on every saved tiny case for every seed and budget.
- Optional PNG plotting could not execute: matplotlib is not installed in the
  available Python environment. The CLI saved the schedule before that error.

Commands used with the bundled Python interpreter:

```console
python generate_instances.py
python -m unittest discover -s tests -v
python main.py experiments
python main.py solve tests/instances/tiny_three.json --algorithm exact --output results/tiny_three_exact.json
python main.py solve tests/instances/gym_10_high.json --seed 2 --iterations 5000 --output results/gym_10_high_sa.json --plot-dir results/plots
python verify_results.py
```

The CSV runtimes exclude validation and output writing. Their sum is
39.306 seconds.
Large-instance results remain unproven best observed values.
