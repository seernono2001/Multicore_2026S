#!/usr/bin/env python3
import csv
import math
import random
import statistics
from collections import Counter
########################################################################
# Parameters
########################################################################
'''
Random Parameter Generator
- Generates csv file with problem size and thread count
- Problem size is log-uniformly distributed between 1,000 and 100,000,000
- Thread counts are powers of 2 from 2 to 64 as supported by Crunchy3
'''
NUM_CONFIGS = 1000 # total number of configurations to generate
PROBLEM_MIN = 1000
PROBLEM_MAX = 100000000
MAX_THREADS = 64
CSV_FILE = "random_configs.csv"
SUMMARY_CSV = "summary_stats.csv"

########################################################################
# Random Problem Size Generator (log-uniform distribution)
########################################################################
'''
Log Uniform Distribution between 1000 to 100 million
'''
def random_problem_size() -> int:
    return int(round(10 ** random.uniform(math.log10(PROBLEM_MIN), math.log10(PROBLEM_MAX))))

########################################################################
# Base configurations
########################################################################
'''
Each configuration is a tuple of (problem_size, thread_count)
'''
base_configs = set()

while len(base_configs) < NUM_CONFIGS:
    ps = random_problem_size()
    th = random.randint(1, MAX_THREADS)
    base_configs.add((ps, th))

base_configs = sorted(base_configs)

########################################################################
# Write to CSV
########################################################################
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Index", "ProblemSize", "Threads"])
    for idx, (ps, th) in enumerate(base_configs, start=1):
        writer.writerow([idx, ps, th])

print(f"\nGenerated {len(base_configs)} base configs")
print(f"Saved to {CSV_FILE}")

########################################################################
# Summary of parameters
########################################################################
'''
Extract problem sizes and thread counts for summary statistics
'''
problem_sizes = [row[0] for row in base_configs]
threads = [row[1] for row in base_configs]

# Summary of spread of generated parameters to ensure good coverage
def get_summary_dict(values):
    summary = {
        "Count": len(values),
        "Min": min(values),
        "Max": max(values),
        "Mean": round(statistics.mean(values), 2),
        "Median": round(statistics.median(values), 2),
        "StdDev": round(statistics.stdev(values), 2) if len(values) > 1 else 0.00,
    }
    return summary
    
problem_summary = get_summary_dict(problem_sizes)
thread_summary = get_summary_dict(threads)

########################################################################
# Write summary statistics to CSV
########################################################################
with open(SUMMARY_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Variable", "Count", "Min", "Max", "Mean", "Median", "StdDev"])

    writer.writerow([
        "ProblemSize",
        problem_summary["Count"],
        problem_summary["Min"],
        problem_summary["Max"],
        problem_summary["Mean"],
        problem_summary["Median"],
        problem_summary["StdDev"]
    ])

    writer.writerow([
        "Threads",
        thread_summary["Count"],
        thread_summary["Min"],
        thread_summary["Max"],
        thread_summary["Mean"],
        thread_summary["Median"],
        thread_summary["StdDev"]
    ])

########################################################################
# Print results
########################################################################
print(f"Requested random configs: {NUM_CONFIGS}")
print(f"Unique random combos generated: {len(base_configs)}")
print(f"Saved configurations to {CSV_FILE}")
print(f"Saved summary statistics to {SUMMARY_CSV}")

print("\n======= Problem Sizes ========")
for k, v in problem_summary.items():
    print(f"{k}: {v}")

print("\n======= Threads ========")
for k, v in thread_summary.items():
    print(f"{k}: {v}")