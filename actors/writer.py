import ray
import random
import uuid
import time

@ray.remote
class Writer:
    def __init__(self, table_holder):
        self.table_holder = table_holder
        self.total_requests = 0
        self.start_time = time.time()

    def add_row(self):
        # Generate random features and result
        features = [random.random() for _ in range(64)]
        result = random.random()

        # Add row to the table
        row_id = ray.get(self.table_holder.add_row.remote(features, result))

        # Increment total requests
        self.total_requests += 1

        # Deposit UUID into a set in the Ray object store
        ray.get(self.table_holder.uuids.add.remote(row_id))

    def run(self, rows_per_second):
        while True:
            start_time = time.time()
            for _ in range(rows_per_second):
                self.add_row()
            elapsed_time = time.time() - start_time
            time.sleep(max(0, 1 - elapsed_time))
            self.print_stats()

    def print_stats(self):
        elapsed_time = time.time() - self.start_time
        requests_per_second = self.total_requests / elapsed_time
        print(f"Total requests: {self.total_requests}, Requests per second: {requests_per_second:.2f}")
