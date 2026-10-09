"""Validated instances, append decoding, and independent schedule checks."""
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class Exercise:
    equipment: str
    duration: int


@dataclass(frozen=True)
class Person:
    id: str
    exercises: tuple[Exercise, ...]


@dataclass(frozen=True)
class Instance:
    name: str
    people: tuple[Person, ...]

    @property
    def equipment(self):
        return sorted({e.equipment for p in self.people for e in p.exercises})

    @property
    def operation_count(self):
        return sum(len(p.exercises) for p in self.people)


@dataclass(frozen=True)
class Operation:
    person: int
    exercise: int
    equipment: str
    start: int
    end: int


@dataclass
class Schedule:
    operations: list[Operation]
    waiting: list[int]
    total_waiting: int
    makespan: int


def parse_instance(data):
    if not isinstance(data, dict):
        raise ValueError('Input must be a JSON object')
    name = data.get('name', 'unnamed')
    if not isinstance(name, str) or not name.strip():
        raise ValueError('name must be a nonempty string')
    raw = data.get('people')
    if not isinstance(raw, list) or not raw:
        raise ValueError('people must be a nonempty list')
    people, ids = [], set()
    for p in raw:
        if not isinstance(p, dict):
            raise ValueError('Each person must be an object')
        pid = p.get('id')
        if not isinstance(pid, str) or not pid.strip() or pid in ids:
            raise ValueError('Person IDs must be unique nonempty strings')
        ids.add(pid)
        exercises = p.get('exercises')
        if not isinstance(exercises, list) or not exercises:
            raise ValueError('Each person needs a nonempty exercises list')
        parsed = []
        for e in exercises:
            if not isinstance(e, dict):
                raise ValueError('Each exercise must be an object')
            equipment, duration = e.get('equipment'), e.get('duration')
            if not isinstance(equipment, str) or not equipment.strip():
                raise ValueError('equipment must be a nonempty string')
            if type(duration) is not int or duration <= 0:
                raise ValueError('duration must be a positive integer (not boolean)')
            parsed.append(Exercise(equipment, duration))
        people.append(Person(pid, tuple(parsed)))
    return Instance(name, tuple(people))


def load_instance(path):
    return parse_instance(json.loads(Path(path).read_text(encoding='utf-8')))


def baseline_priority(instance):
    """Round robin in input order; skip people who have finished."""
    return [i for k in range(max(len(p.exercises) for p in instance.people))
            for i, p in enumerate(instance.people) if k < len(p.exercises)]


def decode(instance, priority):
    expected = Counter({i: len(p.exercises) for i, p in enumerate(instance.people)})
    if any(type(i) is not int for i in priority) or Counter(priority) != expected:
        raise ValueError('Priority must contain each person index once per exercise')
    next_exercise = [0] * len(instance.people)
    ready = [0] * len(instance.people)
    equipment_ready = defaultdict(int)
    operations = []
    for i in priority:
        k = next_exercise[i]
        e = instance.people[i].exercises[k]
        start = max(ready[i], equipment_ready[e.equipment])
        end = start + e.duration
        operations.append(Operation(i, k, e.equipment, start, end))
        ready[i] = equipment_ready[e.equipment] = end
        next_exercise[i] += 1
    waiting = [ready[i] - sum(e.duration for e in p.exercises)
               for i, p in enumerate(instance.people)]
    return Schedule(operations, waiting, sum(waiting), max(ready))


def verify_schedule(instance, schedule):
    """Recompute all constraints and metrics from operation intervals."""
    expected = {(i, k) for i, p in enumerate(instance.people)
                for k in range(len(p.exercises))}
    seen, by_person, by_equipment = set(), defaultdict(list), defaultdict(list)
    for op in schedule.operations:
        key = (op.person, op.exercise)
        if key not in expected or key in seen:
            raise ValueError('Missing, duplicate, or unknown exercise')
        seen.add(key)
        e = instance.people[op.person].exercises[op.exercise]
        if (type(op.start) is not int or type(op.end) is not int or op.start < 0
                or op.equipment != e.equipment or op.end - op.start != e.duration):
            raise ValueError('Invalid equipment, time, or duration')
        by_person[op.person].append(op)
        by_equipment[op.equipment].append(op)
    if seen != expected:
        raise ValueError('Every exercise must be scheduled exactly once')
    waiting, completions = [], []
    for i in range(len(instance.people)):
        previous, wait = 0, 0
        for op in sorted(by_person[i], key=lambda op: op.exercise):
            if op.start < previous:
                raise ValueError('Person overlap or fixed-order violation')
            wait += op.start - previous
            previous = op.end
        waiting.append(wait)
        completions.append(previous)
    for ops in by_equipment.values():
        ordered = sorted(ops, key=lambda op: op.start)
        if any(a.end > b.start for a, b in zip(ordered, ordered[1:])):
            raise ValueError('Equipment overlap')
    if (waiting != schedule.waiting or sum(waiting) != schedule.total_waiting
            or max(completions) != schedule.makespan):
        raise ValueError('Incorrect reported metrics')
    return True


def schedule_dict(instance, schedule):
    return {'instance': instance.name, 'total_waiting': schedule.total_waiting,
            'makespan': schedule.makespan,
            'waiting_by_person': {p.id: schedule.waiting[i]
                                  for i, p in enumerate(instance.people)},
            'operations': [dict(person=instance.people[o.person].id,
                                exercise=o.exercise + 1, equipment=o.equipment,
                                start=o.start, end=o.end) for o in schedule.operations]}
