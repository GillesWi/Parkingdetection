import datetime
import time


def start_timer():
    current_time = time.perf_counter()
    return datetime.datetime.fromtimestamp(current_time) if current_time else None


def get_elapsed_time(start_time):
    if start_time is None:
        return 0

    current_time = time.perf_counter()
    start_timestamp = time.mktime(start_time.timetuple())
    elapsed_time = current_time - start_timestamp
    return elapsed_time
