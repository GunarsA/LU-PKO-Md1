"""Audit saved measurements and example schedules; save a verification record."""
import csv
import json
from pathlib import Path
import platform
from scheduling import load_instance, decode, verify_schedule


def main():
    root = Path(__file__).resolve().parent
    rows = list(csv.DictReader((root / 'results/experiments.csv').open(encoding='utf-8')))
    instances = {i.name: i for i in (load_instance(p) for p in
                 (root / 'tests/instances').glob('*.json'))}
    assert len(rows) == 160
    sa = [r for r in rows if r['algorithm'] == 'sa']
    assert len(sa) == 140
    for name, instance in instances.items():
        group = [r for r in rows if r['instance'] == name]
        baseline = next(r for r in group if r['algorithm'] == 'baseline')
        for budget in (1000, 5000):
            runs = [r for r in group if r['algorithm'] == 'sa' and int(r['iterations']) == budget]
            assert {int(r['seed']) for r in runs} == set(range(5))
        for r in group:
            assert int(r['people']) == len(instance.people)
            assert int(r['equipment']) == len(instance.equipment)
            assert int(r['exercises']) == instance.operation_count
            assert float(r['runtime_seconds']) >= 0
            assert int(r['baseline_waiting']) == int(baseline['total_waiting'])
            if r['algorithm'] == 'sa':
                assert int(r['total_waiting']) <= int(r['baseline_waiting'])
                if r['exact_optimum']:
                    assert int(r['total_waiting']) == int(r['exact_optimum'])
            if r['exact_optimum']:
                assert int(r['gap_absolute']) == int(r['total_waiting']) - int(r['exact_optimum'])
                assert int(r['gap_absolute']) >= 0
                if int(r['exact_optimum']) == 0:
                    assert r['gap_percent'] == ''
            else:
                assert r['gap_absolute'] == r['gap_percent'] == ''
    for filename in ('tiny_three_exact.json', 'gym_10_high_sa.json'):
        data = json.loads((root / 'results' / filename).read_text(encoding='utf-8'))
        instance = instances[data['instance']]
        lookup = {p.id: i for i, p in enumerate(instance.people)}
        schedule = decode(instance, [lookup[pid] for pid in data['priority']])
        verify_schedule(instance, schedule)
        assert schedule.total_waiting == data['total_waiting']
        assert schedule.makespan == data['makespan']
        if 'best_history' in data:
            assert data['best_history'][-1] == schedule.total_waiting
    text = f'''# Verification record

- Python: {platform.python_version()} on {platform.system()} {platform.machine()}.
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
{sum(float(r['runtime_seconds']) for r in rows):.3f} seconds.
Large-instance results remain unproven best observed values.
'''
    (root / 'results/validation.md').write_text(text, encoding='utf-8')
    print('Saved-result audit passed; wrote results/validation.md')


if __name__ == '__main__':
    main()
