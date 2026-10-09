"""Tiny-instance branch and bound; see README for completeness proof."""
from dataclasses import dataclass
import math
from time import perf_counter
from scheduling import Schedule, baseline_priority, decode


@dataclass
class ExactResult:
    priority: list[int]
    schedule: Schedule
    optimal: bool
    nodes: int
    reason: str


def solve_exact(instance, max_nodes=1000000, time_limit=10.0):
    if type(max_nodes) is not int or max_nodes < 1:
        raise ValueError('max_nodes must be a positive integer')
    if not math.isfinite(time_limit) or time_limit <= 0:
        raise ValueError('time_limit must be finite and positive')
    best = baseline_priority(instance)
    best_schedule = decode(instance, best)
    if best_schedule.total_waiting == 0:
        return ExactResult(best, best_schedule, True, 0, 'zero lower bound reached')
    next_op = [0] * len(instance.people)
    ready = [0] * len(instance.people)
    equipment_ready = {e: 0 for e in instance.equipment}
    prefix, nodes = [], 0
    deadline = perf_counter() + time_limit
    reason = 'search completed'

    class LimitReached(Exception):
        pass

    def visit(wait_so_far):
        nonlocal nodes, best, best_schedule, reason
        if nodes >= max_nodes or perf_counter() >= deadline:
            reason = 'node limit reached' if nodes >= max_nodes else 'time limit reached'
            raise LimitReached
        nodes += 1
        # Accumulated waiting never decreases in an append extension.
        if wait_so_far >= best_schedule.total_waiting:
            return
        if len(prefix) == instance.operation_count:
            best = prefix.copy()
            best_schedule = decode(instance, best)
            return
        for i, p in enumerate(instance.people):
            k = next_op[i]
            if k == len(p.exercises):
                continue
            e = p.exercises[k]
            old_person, old_equipment = ready[i], equipment_ready[e.equipment]
            start = max(old_person, old_equipment)
            ready[i] = equipment_ready[e.equipment] = start + e.duration
            next_op[i] += 1
            prefix.append(i)
            visit(wait_so_far + start - old_person)
            prefix.pop()
            next_op[i] -= 1
            ready[i], equipment_ready[e.equipment] = old_person, old_equipment

    optimal = True
    try:
        visit(0)
    except (LimitReached, KeyboardInterrupt):
        optimal = False
        if reason == 'search completed':
            reason = 'interrupted'
    return ExactResult(best, best_schedule, optimal, nodes, reason)
