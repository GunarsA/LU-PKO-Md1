"""Optional matplotlib output; no plotting dependency needed for solvers."""
from pathlib import Path

# Matplotlib's tab20 colors, kept explicit for compatibility with type stubs.
PERSON_COLORS = (
    '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a',
    '#d62728', '#ff9896', '#9467bd', '#c5b0d5', '#8c564b', '#c49c94',
    '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7', '#bcbd22', '#dbdb8d',
    '#17becf', '#9edae5',
)


def plot_result(instance, schedule, history, output_dir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    equipment = instance.equipment
    fig, ax = plt.subplots(figsize=(12, max(3, len(equipment) * 0.6)))
    for op in schedule.operations:
        y = equipment.index(op.equipment)
        ax.barh(y, op.end - op.start, left=op.start,
                color=PERSON_COLORS[op.person % len(PERSON_COLORS)],
                edgecolor='black', linewidth=0.4)
        ax.text((op.start + op.end) / 2, y,
                f'{instance.people[op.person].id}:{op.exercise + 1}',
                ha='center', va='center', fontsize=7)
    ax.set_yticks(range(len(equipment)), equipment)
    ax.set_xlabel('Time (minutes)')
    ax.set_title(f'{instance.name}: waiting {schedule.total_waiting}, makespan {schedule.makespan}')
    fig.tight_layout()
    fig.savefig(str(out / 'gantt.png'), dpi=160)
    plt.close(fig)
    if history is not None:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(range(len(history)), history)
        ax.set(xlabel='SA iteration', ylabel='Best total waiting (minutes)',
               title=instance.name)
        fig.tight_layout()
        fig.savefig(str(out / 'convergence.png'), dpi=160)
        plt.close(fig)
