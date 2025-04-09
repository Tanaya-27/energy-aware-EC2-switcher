import time
import numpy as np

def high_cpu_memory_usage(size):
    # create a large array of random numbers
    data = np.random.rand(size)

    # perform a computation that will consume CPU
    while True:
        # calculate the sum of squares
        result = np.sum(data ** 2)
        print(f"Current result: {result}")
        time.sleep(1)  # sleep to slow down the output

if __name__ == "__main__":
    # adjust the size to increase/decrease resource utilization
    size = 10**7  #change this value to increase/decrease utilization
    print(f"Starting high CPU and memory usage with array size: {size}")
    high_cpu_memory_usage(size)
