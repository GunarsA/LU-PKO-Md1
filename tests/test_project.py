"""Meaningful unit checks and an independent exactness oracle."""
from collections import defaultdict
from dataclasses import replace
from itertools import permutations, product
from pathlib import Path
import random
import unittest
from annealing import anneal, neighbor
from exact import solve_exact
from scheduling import (parse_instance, load_instance, decode, baseline_priority,
                        verify_schedule, Schedule)


ROOT = Path(__file__).resolve().parent / 'instances'


def machine_order_optimum(instance):
    """Independent oracle: enumerate equipment permutations and evaluate DAGs."""
    operations = {(i, k): e for i, p in enumerate(instance.people)
                  for k, e in enumerate(p.exercises)}
    equipment = defaultdict(list)
    job_edges = []
    for (i, k), e in operations.items():
        equipment[e.equipment].append((i, k))
        if k:
            job_edges.append(((i, k - 1), (i, k)))
    best = float('inf')
    for orders in product(*(list(permutations(ops)) for ops in equipment.values())):
        predecessors = {op: set() for op in operations}
        edges = job_edges + [(a, b) for order in orders for a, b in zip(order, order[1:])]
        for a, b in edges:
            predecessors[b].add(a)
        ends, remaining = {}, set(operations)
        while remaining:
            available = [op for op in remaining if predecessors[op] <= ends.keys()]
            if not available:
                break  # Cyclic equipment orders are infeasible.
            for op in available:
                ends[op] = max((ends[p] for p in predecessors[op]), default=0) + operations[op].duration
                remaining.remove(op)
        if not remaining:
            value = sum(ends[(i, len(p.exercises) - 1)]
                        - sum(e.duration for e in p.exercises)
                        for i, p in enumerate(instance.people))
            best = min(best, value)
    return best


class SchedulingTests(unittest.TestCase):
    def test_manual_optima(self):
        for name, expected in [('one_person', 0), ('no_conflicts', 0),
                               ('manual_conflict', 1), ('tiny_cross', 0)]:
            with self.subTest(name=name):
                instance = load_instance(ROOT / f'{name}.json')
                result = solve_exact(instance)
                self.assertTrue(result.optimal)
                self.assertEqual(result.schedule.total_waiting, expected)
                verify_schedule(instance, result.schedule)
        instance = load_instance(ROOT / 'manual_conflict.json')
        self.assertEqual(decode(instance, baseline_priority(instance)).total_waiting, 3)

    def test_exact_independent_oracle(self):
        for name in ['tiny_repeated', 'tiny_three']:
            instance = load_instance(ROOT / f'{name}.json')
            result = solve_exact(instance)
            self.assertTrue(result.optimal)
            self.assertEqual(result.schedule.total_waiting, machine_order_optimum(instance))
        rng = random.Random(72)
        for trial in range(12):
            instance = parse_instance({'people': [
                {'id': str(i), 'exercises': [dict(equipment=rng.choice('AB'), duration=rng.randint(1, 4))
                                           for _ in range(2)]} for i in range(3)]})
            result = solve_exact(instance)
            self.assertTrue(result.optimal, trial)
            self.assertEqual(result.schedule.total_waiting, machine_order_optimum(instance), trial)

    def test_all_saved_instances_and_neighbors(self):
        rng = random.Random(1)
        for path in ROOT.glob('*.json'):
            instance = load_instance(path)
            priority = baseline_priority(instance)
            for _ in range(12):
                priority = neighbor(priority, rng)
                verify_schedule(instance, decode(instance, priority))

    def test_append_does_not_insert_in_gap(self):
        instance = parse_instance({'people': [
            {'id': 'a', 'exercises': [dict(equipment='A', duration=5), dict(equipment='B', duration=2)]},
            {'id': 'b', 'exercises': [dict(equipment='B', duration=1)]}]})
        schedule = decode(instance, [0, 0, 1])
        self.assertEqual(schedule.operations[-1].start, 7)
        self.assertEqual(decode(instance, [1, 0, 0]).total_waiting, 0)

    def test_sa_reproducibility_and_best_tracking(self):
        instance = load_instance(ROOT / 'tiny_three.json')
        for seed in range(5):
            a = anneal(instance, 300, seed)
            b = anneal(instance, 300, seed)
            self.assertEqual(a, b)
            self.assertLessEqual(a.schedule.total_waiting, a.initial_waiting)
            self.assertTrue(all(x >= y for x, y in zip(a.history, a.history[1:])))
            self.assertEqual(len(a.history), 301)
            self.assertEqual(a.history[-1], a.schedule.total_waiting)
            verify_schedule(instance, a.schedule)
        self.assertEqual(anneal(instance, 0).schedule, decode(instance, baseline_priority(instance)))
        self.assertGreater(anneal(instance, 300, 0, 1000, 1000).accepted_worse, 0)

    def test_exact_limits_never_claim_optimal(self):
        instance = load_instance(ROOT / 'manual_conflict.json')
        result = solve_exact(instance, max_nodes=1)
        self.assertFalse(result.optimal)
        self.assertEqual(result.reason, 'node limit reached')
        verify_schedule(instance, result.schedule)
        result = solve_exact(instance, time_limit=1e-12)
        self.assertFalse(result.optimal)
        self.assertEqual(result.reason, 'time limit reached')

    def test_invalid_inputs(self):
        for value in [None, {}, {'people': []}, {'people': [None]},
                      {'people': [{'id': 'x', 'exercises': []}]}]:
            with self.assertRaises(ValueError):
                parse_instance(value)
        for duration in [True, False, 0, -1, 2.5, '3', None]:
            with self.assertRaises(ValueError):
                parse_instance({'people': [{'id': 'x', 'exercises': [
                    dict(equipment='A', duration=duration)]}]})
        person = {'id': 'x', 'exercises': [dict(equipment='A', duration=1)]}
        with self.assertRaises(ValueError):
            parse_instance({'people': [person, person]})
        instance = load_instance(ROOT / 'manual_conflict.json')
        for priority in [[0], [0, 0], [0, 2], [False, 1], [0, '1']]:
            with self.assertRaises(ValueError):
                decode(instance, priority)
        for kwargs in [dict(iterations=-1), dict(temperature=0),
                       dict(temperature=float('nan')), dict(final_temperature=100)]:
            with self.assertRaises(ValueError):
                anneal(instance, **kwargs)

    def test_verifier_rejects_corruption(self):
        instance = load_instance(ROOT / 'manual_conflict.json')
        schedule = decode(instance, [0, 1])
        corrupt = [
            Schedule(schedule.operations[:-1], schedule.waiting, schedule.total_waiting, schedule.makespan),
            Schedule(schedule.operations + schedule.operations[:1], schedule.waiting, schedule.total_waiting, schedule.makespan),
            replace(schedule, total_waiting=999),
            replace(schedule, operations=[schedule.operations[0], replace(schedule.operations[1], start=0, end=1)]),
            replace(schedule, operations=[replace(schedule.operations[0], end=4), schedule.operations[1]])]
        for bad in corrupt:
            with self.assertRaises(ValueError):
                verify_schedule(instance, bad)
        instance = load_instance(ROOT / 'one_person.json')
        schedule = decode(instance, [0, 0, 0])
        with self.assertRaises(ValueError):
            verify_schedule(instance, replace(schedule, operations=[schedule.operations[0],
                replace(schedule.operations[1], start=0, end=2), schedule.operations[2]]))


if __name__ == '__main__':
    unittest.main()
