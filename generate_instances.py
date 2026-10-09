"""Reproduce the saved input data with only the standard library."""
import json
from pathlib import Path
import random


def save(name, workouts):
    data = {'name': name, 'people': [
        {'id': f'P{i + 1}', 'exercises': [dict(equipment=e, duration=d) for e, d in workout]}
        for i, workout in enumerate(workouts)]}
    out = Path('tests/instances')
    out.mkdir(parents=True, exist_ok=True)
    (out / f'{name}.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def main():
    save('one_person', [[('A', 3), ('B', 2), ('A', 4)]])
    save('no_conflicts', [[('A', 2), ('B', 3)], [('C', 4), ('D', 2)]])
    save('manual_conflict', [[('A', 3)], [('A', 1)]])
    save('tiny_cross', [[('A', 2), ('B', 1)], [('B', 2), ('A', 1)]])
    save('tiny_repeated', [[('A', 2), ('B', 1), ('A', 1)], [('A', 1), ('B', 2)]])
    save('tiny_three', [[('A', 2), ('B', 2)], [('B', 1), ('A', 3)], [('A', 1), ('B', 1)]])
    for people, machines, contention in [(5, 8, 'low'), (5, 2, 'high'),
                                          (10, 8, 'low'), (10, 3, 'high'),
                                          (20, 10, 'low'), (20, 3, 'high'),
                                          (30, 12, 'low'), (30, 4, 'high')]:
        rng = random.Random(20261008 + people * 100 + machines)
        workouts = [[(f'E{rng.randrange(machines) + 1}', rng.randint(1, 10))
                     for _ in range(rng.randint(3, 8))] for _ in range(people)]
        save(f'gym_{people:02d}_{contention}', workouts)


if __name__ == '__main__':
    main()
