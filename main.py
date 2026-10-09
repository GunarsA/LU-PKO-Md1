"""Command-line entry point."""
import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any
from annealing import anneal
from exact import solve_exact
from experiments import run_experiments
from scheduling import load_instance, baseline_priority, decode, verify_schedule, schedule_dict


def main():
    parser = argparse.ArgumentParser(description='Fixed-order gym scheduling: minimize total waiting')
    commands = parser.add_subparsers(dest='command', required=True)
    solve = commands.add_parser('solve')
    solve.add_argument('instance')
    solve.add_argument('--algorithm', choices=['baseline', 'sa', 'exact'], default='sa')
    solve.add_argument('--seed', type=int, default=0)
    solve.add_argument('--iterations', type=int, default=5000)
    solve.add_argument('--temperature', type=float, default=50.0)
    solve.add_argument('--final-temperature', type=float, default=0.1)
    solve.add_argument('--max-nodes', type=int, default=1000000)
    solve.add_argument('--time-limit', type=float, default=10.0)
    solve.add_argument('--output', default='results/solution.json')
    solve.add_argument('--plot-dir')
    exp = commands.add_parser('experiments')
    exp.add_argument('--instances', default='tests/instances')
    exp.add_argument('--output-dir', default='results')
    exp.add_argument('--budgets', type=int, nargs='+', default=[1000, 5000])
    exp.add_argument('--seeds', type=int, nargs='+', default=[0, 1, 2, 3, 4])
    exp.add_argument('--temperature', type=float, default=50.0)
    exp.add_argument('--final-temperature', type=float, default=0.1)
    exp.add_argument('--exact-operations', type=int, default=10)
    exp.add_argument('--exact-nodes', type=int, default=1000000)
    exp.add_argument('--exact-seconds', type=float, default=10.0)
    args = parser.parse_args()
    try:
        if args.command == 'experiments':
            run_experiments(args.instances, args.output_dir, args.budgets, args.seeds,
                            args.temperature, args.final_temperature, args.exact_operations,
                            args.exact_nodes, args.exact_seconds)
            return
        instance = load_instance(args.instance)
        history = None
        start = perf_counter()
        metadata: dict[str, Any] = {'algorithm': args.algorithm}
        exact_result = None
        if args.algorithm == 'sa':
            sa_result = anneal(instance, args.iterations, args.seed, args.temperature, args.final_temperature)
            schedule, priority, history = sa_result.schedule, sa_result.priority, sa_result.history
            metadata.update(seed=args.seed, iterations=args.iterations, temperature=args.temperature,
                            final_temperature=args.final_temperature,
                            initial_waiting=sa_result.initial_waiting, accepted=sa_result.accepted,
                            accepted_worse=sa_result.accepted_worse, best_history=history)
        elif args.algorithm == 'exact':
            exact_result = solve_exact(instance, args.max_nodes, args.time_limit)
            schedule, priority = exact_result.schedule, exact_result.priority
            metadata.update(optimal=exact_result.optimal, status=exact_result.reason, nodes=exact_result.nodes,
                            max_nodes=args.max_nodes, time_limit=args.time_limit)
        else:
            priority = baseline_priority(instance)
            schedule = decode(instance, priority)
        metadata['runtime_seconds'] = perf_counter() - start
        verify_schedule(instance, schedule)
        payload = schedule_dict(instance, schedule)
        payload.update(metadata, priority=[instance.people[i].id for i in priority])
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
        print(f'{instance.name}: total waiting={schedule.total_waiting}, makespan={schedule.makespan}')
        if exact_result is not None:
            print(f'Proven optimal: {exact_result.optimal}; {exact_result.reason}; nodes={exact_result.nodes}')
        print(f'Saved {out}')
        if args.plot_dir:
            from plotting import plot_result
            plot_result(instance, schedule, history, args.plot_dir)
    except (ValueError, OSError, ImportError, RecursionError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
