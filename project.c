#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>
#include <string.h>
#include <math.h>

void sequential_compute(double *A, double *B, double *C, int n);
void sequential_stream(double *A, double *B, double *C, int n);
void sequential_barrier_heavy(double *A, int n);
void parallel_compute(double *A, double *B, double *C, int n);
void parallel_stream(double *A, double *B, double *C, int n);
void parallel_barrier_heavy(double *A, int n);
void check_result(double *sequential_result, double *parallel_result, int n);

void sequential_compute(double *A, double *B, double *C, int n) {
	for (int i = 0; i < n; i++) {
		C[i] = A[i] * B[i] + sqrt(A[i]);
	}
}

void sequential_stream(double *A, double *B, double *C, int n) {
    for (int i = 0; i < n; i++) {
        C[i] = A[i] + 0.5 * B[i];
    }
}

void sequential_barrier_heavy(double *A, int n) {
	double *temp = (double*)calloc(n, sizeof(double));
	memcpy((void *)temp, (void *) A, n * sizeof(double));
	for (int s = 0; s < 200; s++) {
		for (int i = 1; i < n-1; i++) {
			temp[i] = (A[i-1] + A[i] + A[i+1]) / 3.0;
		}
	}
	memcpy((void *)A, (void *) temp, n * sizeof(double));
	free(temp);
}

void parallel_compute(double *A, double *B, double *C, int n) {
    #pragma omp parallel for
    for (int i = 0; i < n; i++) {
        C[i] = A[i] * B[i] + sqrt(A[i]);
    }
}

void parallel_stream(double *A, double *B, double *C, int n) {
    #pragma omp parallel for
    for (int i = 0; i < n; i++) {
        C[i] = A[i] + 0.5 * B[i];
    }
}

void parallel_barrier_heavy(double *A, int n) {
	double *p_temp = (double*)calloc(n, sizeof(double));
	memcpy((void *)p_temp, (void *) A, n * sizeof(double));

    #pragma omp parallel
    {
        for (int s = 0; s < 200; s++) {
            #pragma omp for
            for (int i = 1; i < n-1; i++) {
                p_temp[i] = (A[i-1] + A[i] + A[i+1]) / 3.0;
            }
            #pragma omp barrier
        }
    }
    memcpy((void *)A, (void *)p_temp, n * sizeof(double));
    free(p_temp);
}

void check_result(double *sequential_result, double *parallel_result, int n) {
	for (int i = 0; i < n; i++) {
		if (sequential_result[i] != parallel_result[i]) {
			printf("Mismatch at index %d: sequential = %lf, parallel = %lf\n", i, sequential_result[i], parallel_result[i]);
		}
	}
	printf("Result is correct!\n");
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        printf("usage: ./project num threads operation\n");
        printf("  num: size of the array\n");
        printf("  threads: number of threads\n");
        printf("  operation type: 0=compute, 1=stream, 2=barrier_heavy\n");
        exit(1);
    }

	long num = atol(argv[1]);   /* array size */
    int threads = atoi(argv[2]);     /* number of threads */
    int operation = atoi(argv[3]);  /* operation type */
	double sq_time_taken, parallel_time_taken;
	double start, end;

	double *a= (double*)calloc(num, sizeof(double));
	double *b= (double*)calloc(num, sizeof(double));
	double *c= (double*)calloc(num, sizeof(double));
	double *sequential_result = (double*)calloc(num, sizeof(double));

	//Fill out arrays a and b with some random numbers
	srand(time(0));
	for (int i = 0; i < num; i++) {
		a[i] = rand() % num;
		b[i] = rand() % num;
	}

	for (int i = 0; i < num; i++) {
		c[i] = 0;
	}

	switch(operation) {
		case 0:
			// Run parallel version
			printf("Running compute with %d threads...\n", threads);
			start = omp_get_wtime();
			omp_set_num_threads(threads);
			parallel_compute(a, b, c, num);
			end = omp_get_wtime();
			parallel_time_taken = end - start;

			// Run sequential version
			printf("Running compute sequentially\n");
			start = omp_get_wtime();
			sequential_compute(a, b, sequential_result, num);
			end = omp_get_wtime();
			sq_time_taken = end - start;

			// Check results
			check_result(sequential_result, c, num);

			break;
		case 1:
			// Run parallel version
			printf("Running stream with %d threads...\n", threads);
			start = omp_get_wtime();
			omp_set_num_threads(threads);
			parallel_stream(a, b, c, num);
			end = omp_get_wtime();
			parallel_time_taken = end - start;

			// Run sequential version
			printf("Running stream sequentially\n");
			start = omp_get_wtime();
			sequential_stream(a, b, sequential_result, num);
			end = omp_get_wtime();
			sq_time_taken = end - start;

			// Check results
			check_result(sequential_result, c, num);

			break;
		case 2:
			// Run parallel version
			printf("Running barrier heavy with %d threads...\n", threads);
			memcpy(sequential_result, a, num * sizeof(double));

			start = omp_get_wtime();
			omp_set_num_threads(threads);
			parallel_barrier_heavy(a, num);
			end = omp_get_wtime();
			parallel_time_taken = end - start;
			
			// Run sequential version
			printf("Running barrier heavy sequentially\n");
			start = omp_get_wtime();
			sequential_barrier_heavy(sequential_result, num);
			end = omp_get_wtime();
			sq_time_taken = end - start;

			// Check results
			check_result(sequential_result, a, num);
			
			break;
		default:
			printf("Invalid operation type. Use 0 for compute, 1 for stream, or 2 for barrier_heavy.\n");
			exit(1);
	}
	
	printf("array_size=%ld threads=%d operation=%d sq_time=%f par_time=%f speedup=%f\n",
			num, threads, operation,
			sq_time_taken, parallel_time_taken, sq_time_taken / parallel_time_taken);

	free(a); free(b); free(c); free(sequential_result);
    return 0;
}
