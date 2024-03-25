# file: factorize_numbers.py

import multiprocessing
import time

# Function for factorizing a number
def factorize(num):
    factors = []
    for i in range(1, num + 1):
        if num % i == 0:
            factors.append(i)
    return factors

# Function for factorizing numbers synchronously
def factorize_sync(*numbers):
    results = []
    start_time = time.time()
    for num in numbers:
        results.append(factorize(num))
    end_time = time.time()
    print("Synchronous execution time:", end_time - start_time)
    return results

# Function for factorizing numbers in parallel
def factorize_parallel(*numbers):
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    start_time = time.time()
    results = pool.map(factorize, numbers)
    end_time = time.time()
    print("Parallel execution time:", end_time - start_time)
    pool.close()
    pool.join()
    return results

# Example usage
if __name__ == "__main__":
    # Testing the synchronous version
    a_sync, b_sync, c_sync, d_sync = factorize_sync(128, 255, 99999, 10651060)
    print("Synchronously:")
    print(a_sync)
    print(b_sync)
    print(c_sync)
    print(d_sync)
    
    # Testing the version utilizing multiprocessing
    a_parallel, b_parallel, c_parallel, d_parallel = factorize_parallel(128, 255, 99999, 10651060)
    print("\nUsing multiprocessing:")
    print(a_parallel)
    print(b_parallel)
    print(c_parallel)
    print(d_parallel)