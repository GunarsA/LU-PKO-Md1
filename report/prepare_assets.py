"""Rebuild report tables and Latvian figures from saved measured outputs."""
import csv
import json
from pathlib import Path
from statistics import mean
import shutil

import matplotlib.pyplot as plt

plt.switch_backend("Agg")

# Matplotlib's tab10 colors, without depending on colormap registry type hints.
PERSON_COLORS = (
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
)

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
shutil.copyfile(PROJECT / "results/experiments.csv", ASSETS / "experiments.csv")
with (ASSETS / "experiments.csv").open(encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
table = []
for name in sorted({r["instance"] for r in rows if r["instance"].startswith("gym_")}):
    group = [r for r in rows if r["instance"] == name]
    baseline = next(r for r in group if r["algorithm"] == "baseline")
    short = [r for r in group if r["algorithm"] == "sa" and r["iterations"] == "1000"]
    long = [r for r in group if r["algorithm"] == "sa" and r["iterations"] == "5000"]
    assert len(short) == len(long) == 5
    cells = [f'{baseline["people"]} / {"augsta" if name.endswith("high") else "zema"}',
             f'{baseline["equipment"]} / {baseline["exercises"]}', baseline["total_waiting"],
             str(min(int(r["total_waiting"]) for r in short)),
             str(min(int(r["total_waiting"]) for r in long)),
             f'{mean(int(r["total_waiting"]) for r in long):.1f}',
             f'{mean(float(r["runtime_seconds"]) for r in long):.3f}']
    table.extend(f"[{cell.replace('.', ',')}]," for cell in cells)
(ASSETS / "large_table.typ").write_text("(\n" + "\n".join(table) + "\n)", encoding="utf-8")

baseline = json.loads((PROJECT / "results/report/baseline.json").read_text())
sa = json.loads((PROJECT / "results/report/sa.json").read_text())
for name, data in [("baseline", baseline), ("sa", sa)]:
    (ASSETS / f"{name}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    equipment = sorted({op["equipment"] for op in data["operations"]})
    people = sorted(data["waiting_by_person"], key=lambda name: int(name[1:]))
    fig, ax = plt.subplots(figsize=(10, 2.1))
    for op in data["operations"]:
        y = equipment.index(op["equipment"])
        color = PERSON_COLORS[people.index(op["person"]) % len(PERSON_COLORS)]
        ax.barh(y, op["end"] - op["start"], left=op["start"], height=.72,
                color=color, edgecolor="white", linewidth=.5)
        ax.text((op["start"] + op["end"]) / 2, y, op["person"],
                ha="center", va="center", fontsize=6)
    ax.set_yticks(range(len(equipment)), equipment)
    ax.set_xlim(0, max(baseline["makespan"], sa["makespan"]) + 2)
    ax.set_xlabel("Laiks (minūtes)", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=.18)
    fig.tight_layout(pad=.4)
    fig.savefig(str(ASSETS / f"{name}_gantt.png"), dpi=220)
    plt.close(fig)
fig, ax = plt.subplots(figsize=(10, 2.5))
ax.plot(sa["best_history"], color="#083f35", linewidth=1.6)
ax.set(xlabel="SA iterācija", ylabel="Labākā kopējā gaidīšana (min)")
ax.tick_params(labelsize=8)
ax.grid(alpha=.2)
fig.tight_layout(pad=.7)
fig.savefig(str(ASSETS / "convergence.png"), dpi=220)
plt.close(fig)
print("Prepared measured tables and Latvian plots")
