"""Self-written simulated annealing over multiset priority permutations."""
from dataclasses import dataclass
import math
import random
from scheduling import Schedule, baseline_priority, decode


@dataclass
class SAResult:
    priority: list[int]
    schedule: Schedule
    initial_waiting: int
    history: list[int]
    accepted: int
    accepted_worse: int


def neighbor(priority, rng):
    result = priority.copy()
    if len(set(result)) < 2:
        return result
    a = rng.randrange(len(result))
    b = rng.choice([j for j, value in enumerate(result) if value != result[a]])
    if rng.random() < 0.5:
        result[a], result[b] = result[b], result[a]
    else:
        result.insert(b, result.pop(a))
    return result


def anneal(instance, iterations=5000, seed=0, temperature=50.0,
           final_temperature=0.1, initial=None):
    if type(iterations) is not int or iterations < 0:
        raise ValueError('iterations must be a nonnegative integer')
    if not (math.isfinite(temperature) and math.isfinite(final_temperature)
            and 0 < final_temperature <= temperature):
        raise ValueError('Require finite 0 < final_temperature <= temperature')
    rng = random.Random(seed)
    current = list(initial) if initial is not None else baseline_priority(instance)
    current_schedule = decode(instance, current)
    initial_waiting = current_schedule.total_waiting
    best, best_schedule = current.copy(), current_schedule
    history, accepted, accepted_worse = [initial_waiting], 0, 0
    for step in range(iterations):
        # Endpoints included for budgets >= 2; one iteration uses starting T.
        fraction = step / max(1, iterations - 1)
        t = math.exp(math.log(temperature) * (1 - fraction)
                     + math.log(final_temperature) * fraction)
        candidate = neighbor(current, rng)
        candidate_schedule = decode(instance, candidate)
        delta = candidate_schedule.total_waiting - current_schedule.total_waiting
        if delta <= 0 or rng.random() < math.exp(-delta / t):
            current, current_schedule = candidate, candidate_schedule
            accepted += 1
            accepted_worse += int(delta > 0)
            if current_schedule.total_waiting < best_schedule.total_waiting:
                best, best_schedule = current.copy(), current_schedule
        history.append(best_schedule.total_waiting)
    return SAResult(best, best_schedule, initial_waiting, history, accepted, accepted_worse)
