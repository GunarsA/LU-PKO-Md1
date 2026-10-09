# Gym scheduling

A Python command-line program that schedules workouts while preserving each
person's exercise order. It minimizes **total waiting time** and also reports
when the last person finishes (**makespan**).

Everyone arrives at time 0. Each equipment unit serves one person at a time,
exercises run without interruption, and rest, travel, and setup times are ignored.
Different people can exercise simultaneously on different units.

## Setup

Use Python 3.10 or newer. Run commands from the project folder.
No additional packages are needed for solving or experiments. For plots, install:

```console
python -m pip install -r requirements.txt
```

## Solve an instance

Run simulated annealing with a reproducible seed:

```console
python main.py solve tests/instances/gym_10_high.json --seed 2 --iterations 5000
```

The program prints total waiting and makespan in minutes and saves the schedule
to `results/solution.json`. Waiting includes time before the first exercise and
between exercises, summed across everyone; it can exceed makespan.

Choose a different output file:

```console
python main.py solve tests/instances/gym_10_high.json --seed 2 --output results/gym_10_high.json
```

Output JSON contains exercise start/end times, waiting per person, total waiting,
makespan, priorities, runtime, and algorithm settings. SA output also contains
its best objective after each iteration.

### Algorithms

- **`sa`** (default): simulated annealing, starting from the baseline. Returns the
  best schedule found; large-instance results are not guaranteed optimal.
- **`baseline`**: deterministic round-robin priorities in input order, starting
  with everyone's first exercise, then their second, and so on.
- **`exact`**: exhaustive search with branch pruning, intended for tiny instances.
  Its output says whether optimality was proved. A limited or interrupted search
  returns its best schedule with `optimal=false`.

```console
python main.py solve tests/instances/gym_10_high.json --algorithm baseline --output results/baseline.json
python main.py solve tests/instances/manual_conflict.json --algorithm exact --output results/exact.json
```

### Solver options

| Option | Default | Purpose |
|---|---|---|
| `--algorithm` | `sa` | Choose `sa`, `baseline`, or `exact` |
| `--iterations` | `5000` | SA iteration budget; zero returns the initial solution |
| `--seed` | `0` | SA random seed |
| `--temperature` | `50.0` | SA starting temperature |
| `--final-temperature` | `0.1` | SA final temperature |
| `--max-nodes` | `1000000` | Exact-search node limit |
| `--time-limit` | `10.0` | Exact-search time limit in seconds |
| `--output` | `results/solution.json` | Schedule JSON destination |
| `--plot-dir` | none | Save optional PNG plots |

Temperatures must be finite and satisfy `0 < final_temperature <= temperature`.
Seeds reproduce SA schedules for the same input and settings; runtimes vary.
The solver creates output folders as needed and overwrites existing output files.

## Create plots

Add `--plot-dir` to a solve command:

```console
python main.py solve tests/instances/gym_10_high.json --seed 2 --iterations 5000 --output results/sa.json --plot-dir results/sa_plots
```

This creates:

- `gantt.png`: equipment use over time, labeled by person and exercise.
- `convergence.png`: best total waiting versus SA iteration.

Baseline and exact runs produce only the Gantt chart. Use separate plot folders
when comparing runs, since plot filenames are reused.

## Create your own input

Save a JSON file such as `workout.json`:

```json
{
  "name": "my_workout",
  "people": [
    {
      "id": "Alice",
      "exercises": [
        {"equipment": "bike_1", "duration": 3},
        {"equipment": "bench_1", "duration": 2}
      ]
    },
    {
      "id": "Bob",
      "exercises": [
        {"equipment": "bike_1", "duration": 1}
      ]
    }
  ]
}
```

```console
python main.py solve workout.json --seed 2 --output results/my_workout.json
```

The `people` list and each person's `exercises` list must be nonempty. Person IDs
must be unique nonempty strings; equipment names must be nonempty strings and
identify individual units. Durations must be positive integers, not booleans or
fractions. Exercise list order is fixed. `name` is optional.

## Run experiments

Compare the baseline and SA across all saved instances, with exact results for
small instances:

```console
python main.py experiments
```

Defaults use five seeds (`0` to `4`) and two SA budgets (`1000` and `5000`).
Results are saved to `results/experiments.csv` and `results/summary.md`.

To choose budgets, seeds, or a separate output folder:

```console
python main.py experiments --budgets 1000 5000 10000 --seeds 0 1 2 3 4 --output-dir results/comparison
```

Use `--instances` to select another folder of JSON files. Exact search is attempted
only for instances with at most `--exact-operations` exercises (default `10`);
its limits are `--exact-nodes` (default `1000000`) and `--exact-seconds` (default `10`).
SA temperatures can also be changed with `--temperature` and `--final-temperature`.

The CSV records dimensions, settings, seed, algorithm runtime, waiting, makespan,
baseline waiting, proven optimum, and gaps. Runtime excludes validation and file
writing. Optimum/gap fields are blank when optimality is unproven. Percentage gap
is blank for a zero optimum; absolute gap is still recorded. Each experiment run
overwrites the CSV and summary in its selected output folder.

## Tests and example data

```console
python -m unittest discover -s tests -v
```

Tests check exercise order, durations, completeness, resource conflicts, waiting,
reproducibility, and exact-search correctness and limits. Every solved schedule
is also checked before saving.

`tests/instances/` contains six tiny cases and eight larger cases with 5, 10, 20,
and 30 people, including different equipment contention levels.

To regenerate the supplied instances with their fixed generation seeds:

```console
python generate_instances.py
```

This overwrites the supplied instance files. To audit the saved default experiment
batch and the two included sample solutions, run `python verify_results.py`.
That audit is specific to the default batch, not custom experiment settings.

## How scheduling works

A priority list contains each person's ID once per exercise. Each occurrence
schedules that person's next exercise, so workout order is always preserved.
The decoder appends it after both the person's and equipment's previous operation;
it does not insert into earlier equipment gaps.

SA swaps or reinserts priorities, accepts improvements, and sometimes accepts
worse schedules while gradually lowering temperature. It keeps the best schedule
separately. All optimization algorithms are implemented in this project using
the Python standard library; matplotlib is used only for visualization.

## Command help

```console
python main.py solve --help
python main.py experiments --help
```
