# Multicore_2026S
Semester project for Multicore

## Parallel Benchmark Program — project.c

Compile:

`gcc -O2 -fopenmp project.c -o project -lm`

Run commands:

`./project [PROBLEM_SIZE] [NUM_THREADS] [OPERATION]`

For example:

`./project 100 8 2`

Available Operations:

`0=compute`, `1=stream`, and `2=barrier_heavy`

Automation Commands:
- operation number: 0, 1, or 2

`python3 automation.py [operation number]`

It should output something like

```
array_size=100 threads=8 operation=2 sq_time=0.035868  par_time=0.015397 speedup=2.329544717
```
