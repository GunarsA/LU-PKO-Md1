# Measured experiment results

Waiting and makespan are in minutes. Runtime is measured with `time.perf_counter()` on this computer. SA begins with the baseline.

| Instance | Budget | Baseline waiting | Best SA waiting | Mean SA waiting | Mean runtime (s) | Proven optimum |
|---|---:|---:|---:|---:|---:|---:|
| gym_05_high | 1000 | 345 | 118 | 128.6 | 0.1261 |  |
| gym_05_high | 5000 | 345 | 111 | 118.0 | 0.2976 |  |
| gym_05_low | 1000 | 21 | 14 | 14.0 | 0.0532 |  |
| gym_05_low | 5000 | 21 | 14 | 14.0 | 0.2835 |  |
| gym_10_high | 1000 | 605 | 367 | 414.8 | 0.1004 |  |
| gym_10_high | 5000 | 605 | 337 | 377.2 | 0.4664 |  |
| gym_10_low | 1000 | 305 | 143 | 148.4 | 0.1100 |  |
| gym_10_low | 5000 | 305 | 130 | 142.2 | 0.5379 |  |
| gym_20_high | 1000 | 2904 | 2182 | 2366.0 | 0.2527 |  |
| gym_20_high | 5000 | 2904 | 1944 | 2024.2 | 1.0047 |  |
| gym_20_low | 1000 | 1072 | 758 | 812.4 | 0.1987 |  |
| gym_20_low | 5000 | 1072 | 667 | 697.6 | 1.2104 |  |
| gym_30_high | 1000 | 5304 | 4041 | 4265.4 | 0.3517 |  |
| gym_30_high | 5000 | 5304 | 3324 | 3606.6 | 1.5803 |  |
| gym_30_low | 1000 | 2576 | 1580 | 1674.6 | 0.3414 |  |
| gym_30_low | 5000 | 2576 | 1355 | 1395.8 | 1.6217 |  |
| manual_conflict | 1000 | 3 | 1 | 1.0 | 0.0197 | 1 |
| manual_conflict | 5000 | 3 | 1 | 1.0 | 0.0846 | 1 |
| no_conflicts | 1000 | 0 | 0 | 0.0 | 0.0204 | 0 |
| no_conflicts | 5000 | 0 | 0 | 0.0 | 0.1035 | 0 |
| one_person | 1000 | 0 | 0 | 0.0 | 0.0138 | 0 |
| one_person | 5000 | 0 | 0 | 0.0 | 0.1117 | 0 |
| tiny_cross | 1000 | 0 | 0 | 0.0 | 0.0187 | 0 |
| tiny_cross | 5000 | 0 | 0 | 0.0 | 0.1088 | 0 |
| tiny_repeated | 1000 | 2 | 1 | 1.0 | 0.0198 | 1 |
| tiny_repeated | 5000 | 2 | 1 | 1.0 | 0.1001 | 1 |
| tiny_three | 1000 | 5 | 3 | 3.0 | 0.0335 | 3 |
| tiny_three | 5000 | 5 | 3 | 3.0 | 0.1100 | 3 |

Large-instance values are best observed results, not proven optima.
Blank percentage gaps mean the optimum is zero or unproven. Different budgets use the same temperature endpoints, so this compares both iteration count and the resulting cooling rate.
