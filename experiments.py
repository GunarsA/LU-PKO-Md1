"""Run reproducible experiments; write measured results and a summary."""
import csv
from pathlib import Path
from statistics import mean
from time import perf_counter
from annealing import anneal
from exact import solve_exact
from scheduling import Schedule, load_instance, baseline_priority, decode, verify_schedule


def run_experiments(instance_dir, output_dir, budgets=(1000, 5000), seeds=range(5),
                    temperature=50.0, final_temperature=0.1, exact_operations=10,
                    exact_nodes=1000000, exact_seconds=10.0):
    if not budgets or not seeds:
        raise ValueError('Provide at least one budget and seed')
    paths = sorted(Path(instance_dir).glob('*.json'))
    if not paths:
        raise ValueError('No JSON instances found')
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    fields = ['instance', 'people', 'equipment', 'exercises', 'algorithm',
              'iterations', 'temperature', 'final_temperature', 'seed',
              'runtime_seconds', 'total_waiting', 'makespan', 'baseline_waiting',
              'exact_optimum', 'gap_absolute', 'gap_percent', 'exact_status',
              'exact_nodes', 'exact_node_limit', 'exact_time_limit_seconds']
    rows = []
    for path in paths:
        instance = load_instance(path)
        start = perf_counter()
        baseline = decode(instance, baseline_priority(instance))
        baseline_time = perf_counter() - start
        verify_schedule(instance, baseline)
        exact, exact_time = None, None
        if instance.operation_count <= exact_operations:
            start = perf_counter()
            exact = solve_exact(instance, exact_nodes, exact_seconds)
            exact_time = perf_counter() - start
            verify_schedule(instance, exact.schedule)
        optimum = exact.schedule.total_waiting if exact and exact.optimal else None

        def add(algorithm, schedule: Schedule, runtime, **parameters):
            gap = schedule.total_waiting - optimum if optimum is not None else None
            # Percentage is undefined when the optimum is zero.
            percent = (100 * gap / optimum
                       if gap is not None and optimum is not None and optimum > 0
                       else '')
            row = dict(instance=instance.name, people=len(instance.people),
                       equipment=len(instance.equipment), exercises=instance.operation_count,
                       algorithm=algorithm, runtime_seconds=f'{runtime:.9f}',
                       total_waiting=schedule.total_waiting, makespan=schedule.makespan,
                       baseline_waiting=baseline.total_waiting,
                       exact_optimum=optimum if optimum is not None else '',
                       gap_absolute=gap if gap is not None else '', gap_percent=percent,
                       exact_status=exact.reason if exact else 'not attempted',
                       exact_nodes=exact.nodes if exact else '',
                       exact_node_limit=exact_nodes if exact else '',
                       exact_time_limit_seconds=exact_seconds if exact else '')
            row.update(parameters)
            rows.append(row)

        add('baseline', baseline, baseline_time)
        if exact:
            add('exact', exact.schedule, exact_time)
        for budget in budgets:
            for seed in seeds:
                start = perf_counter()
                result = anneal(instance, budget, seed, temperature, final_temperature)
                elapsed = perf_counter() - start
                verify_schedule(instance, result.schedule)
                if result.schedule.total_waiting > result.initial_waiting:
                    raise AssertionError('SA worsened its initial solution')
                add('sa', result.schedule, elapsed, iterations=budget, seed=seed,
                    temperature=temperature, final_temperature=final_temperature)
        print(f'{instance.name}: baseline={baseline.total_waiting}, '
              f'exact={optimum if optimum is not None else "unproven"}', flush=True)
    with (output / 'experiments.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = ['# Measured experiment results', '',
               'Waiting and makespan are in minutes. Runtime is measured with '
               '`time.perf_counter()` on this computer. SA begins with the baseline.', '',
               '| Instance | Budget | Baseline waiting | Best SA waiting | Mean SA waiting | Mean runtime (s) | Proven optimum |',
               '|---|---:|---:|---:|---:|---:|---:|']
    for name in sorted({r['instance'] for r in rows}):
        for budget in budgets:
            group = [r for r in rows if r['instance'] == name
                     and r['algorithm'] == 'sa' and r['iterations'] == budget]
            summary.append(f"| {name} | {budget} | {group[0]['baseline_waiting']} | "
                           f"{min(r['total_waiting'] for r in group)} | "
                           f"{mean(r['total_waiting'] for r in group):.1f} | "
                           f"{mean(float(r['runtime_seconds']) for r in group):.4f} | "
                           f"{group[0]['exact_optimum']} |")
    summary += ['', 'Large-instance values are best observed results, not proven optima.',
                'Blank percentage gaps mean the optimum is zero or unproven. '
                'Different budgets use the same temperature endpoints, so this compares '
                'both iteration count and the resulting cooling rate.', '']
    (output / 'summary.md').write_text('\n'.join(summary), encoding='utf-8')
    return rows
