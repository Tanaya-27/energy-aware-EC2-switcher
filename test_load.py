import threading
import time

def cpu_intensive_task(duration):
    """Simulates a CPU-intensive task for the given duration (in seconds)."""
    end_time = time.time() + duration
    while time.time() < end_time:
        # Perform a computation-heavy operation
        _ = sum(i * i for i in range(10_000))

def run_load_test(threads, duration):
    """Runs multiple threads to simulate high CPU utilization."""
    print(f"Starting load test with {threads} threads for {duration} seconds...")
    thread_list = []
    for _ in range(threads):
        thread = threading.Thread(target=cpu_intensive_task, args=(duration,))
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()
    print("Load test completed.")

if __name__ == "__main__":
    # Adjust the number of threads and duration to control CPU utilization
    threads = int(input("Enter the number of threads (e.g., 2, 4, 8): "))
    duration = int(input("Enter the duration of the test in seconds: "))
    run_load_test(threads, duration)