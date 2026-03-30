#!/usr/bin/env python3
import csv
import statistics
import subprocess
import sys
import re

EXECUTABLE = "./project"
CONFIGURATION_FILE = "random_configs.csv"
REPETITION = 2

def operation_name(op: int) -> str:
    names = {
        0: "compute",
        1: "stream",
        2: "barrier_heavy"
    }
    return names.get(op, f"op{op}")

def safe_stdev(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 automation.py <operation>")
        print("0 = compute, 1 = stream, 2 = barrier_heavy")
        sys.exit(1)

    try:
        OPERATION = int(sys.argv[1])
    except ValueError:
        print("Operation must be 0, 1, or 2")
        sys.exit(1)

    if OPERATION not in [0, 1, 2]:
        print("Invalid operation. Use 0, 1, or 2.")
        sys.exit(1)

    OP_NAME = operation_name(OPERATION)
    RESULTS_FILE = f"results_{OP_NAME}.csv"
    SUMMARY_FILE = f"stat_sum_results_{OP_NAME}.csv"

    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Index",
            "ProblemSize",
            "Threads",
            "Operation",
            "AvgSqTime",
            "AvgParTime",
            "AvgSpeedup"
        ])

    all_problem_sizes = []
    all_threads = []
    all_sq = []
    all_par = []
    all_speed = []

    pattern = re.compile(
        r"array_size=(\d+)\s+threads=(\d+)\s+operation=(\d+)\s+sq_time=([0-9.eE+-]+)\s+par_time=([0-9.eE+-]+)\s+speedup=([0-9.eE+-]+)"
    )

    with open(CONFIGURATION_FILE, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            idx = int(row["Index"])
            ps = int(row["ProblemSize"])
            th = int(row["Threads"])

            print(f"[{idx}] Running: {ps}, {th}, op={OPERATION} ({OP_NAME})")

            sq_times = []
            par_times = []
            speedups = []

            for _ in range(REPETITION):
                result = subprocess.run(
                    [EXECUTABLE, str(ps), str(th), str(OPERATION)],
                    capture_output=True,
                    text=True
                )

                out = result.stdout.strip()
                match = pattern.search(out)

                if not match:
                    print("ERROR parsing output:")
                    print(out)
                    continue

                sq = float(match.group(4))
                par = float(match.group(5))
                sp = float(match.group(6))

                sq_times.append(sq)
                par_times.append(par)
                speedups.append(sp)

            if sq_times:
                avg_sq = sum(sq_times) / len(sq_times)
                avg_par = sum(par_times) / len(par_times)
                avg_sp = sum(speedups) / len(speedups)

                with open(RESULTS_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        idx, ps, th, OPERATION,
                        avg_sq, avg_par, avg_sp
                    ])

                all_problem_sizes.append(ps)
                all_threads.append(th)
                all_sq.append(avg_sq)
                all_par.append(avg_par)
                all_speed.append(avg_sp)

                print(f"Speedup: {avg_sp:.3f}x\n")
            else:
                print("No valid data\n")

    if not all_speed:
        print("No valid results collected. Exiting.")
        sys.exit(1)

    with open(SUMMARY_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Variable", "Count", "Min", "Max", "Mean", "Median", "StdDev"])

        def write_row(name, data):
            writer.writerow([
                name,
                len(data),
                min(data),
                max(data),
                round(statistics.mean(data), 6),
                round(statistics.median(data), 6),
                round(safe_stdev(data), 6)
            ])

        write_row("ProblemSize", all_problem_sizes)
        write_row("Threads", all_threads)
        write_row("AvgSqTime", all_sq)
        write_row("AvgParTime", all_par)
        write_row("AvgSpeedup", all_speed)

    print(f"\nDONE -> {RESULTS_FILE}")
    print(f"SUMMARY -> {SUMMARY_FILE}")

if __name__ == "__main__":
    main()