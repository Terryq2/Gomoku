import time   

class Timer:
    def __init__(self, name: str = ""):
        self.name = name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self  # allows access to .elapsed later

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        elapsed = self.end_time - self.start_time
        if self.name:
            print(f"[{self.name}] Elapsed time: {elapsed:.6f} seconds")
        else:
            print(f"Elapsed time: {elapsed:.6f} seconds")

    @property
    def elapsed(self):
        if self.start_time is None:
            return 0
        end = self.end_time or time.perf_counter()
        return end - self.start_time