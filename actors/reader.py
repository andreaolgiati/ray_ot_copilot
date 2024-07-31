import ray
import time

@ray.remote
class Reader:
    def __init__(self, table_holder):
        self.table_holder = table_holder
        self.total_requests = 0
        self.start_time = time.time()

    def read_rows(self, impression_is_null, num_rows):
        # Select rows based on the user-specified values
        if impression_is_null:
            query = "SELECT * FROM EVENTS WHERE IMPRESSION IS NULL LIMIT ?"
        else:
            query = "SELECT * FROM EVENTS WHERE IMPRESSION IS NOT NULL LIMIT ?"
        rows = self.table_holder.conn.execute(query, (num_rows,)).fetchall()
        self.total_requests += 1
        return rows

    def run(self, rows_per_second, impression_is_null, num_rows):
        while True:
            start_time = time.time()
            for _ in range(rows_per_second):
                self.read_rows(impression_is_null, num_rows)
            elapsed_time = time.time() - start_time
            time.sleep(max(0, 1 - elapsed_time))
            self.print_stats()

    def print_stats(self):
        elapsed_time = time.time() - self.start_time
        requests_per_second = self.total_requests / elapsed_time
        print(f"Total requests: {self.total_requests}, Requests per second: {requests_per_second:.2f}")
