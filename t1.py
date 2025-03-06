from datetime import datetime, timedelta
from collections import defaultdict

# Function to convert path data into edge time intervals
def convert_paths_to_edges(paths, utc_time, time_interval):
    edge_times = defaultdict(list)

    # Iterate over each path with its time offset
    for offset, path in enumerate(paths):
        start_time = utc_time + timedelta(seconds=offset)
        
        # Iterate over consecutive pairs to form edges
        for i in range(len(path) - 1):
            edge = (path[i], path[i + 1])
            edge_times[edge].append(start_time)

    # Convert time list to time ranges
    edge_ranges = defaultdict(list)
    for edge, times in edge_times.items():
        times.sort()
        start = times[0]
        end = times[0]

        for t in times[1:]:
            if t == end + timedelta(seconds=1):
                end = t
            else:
                edge_ranges[edge].append((start, end + timedelta(seconds=1)))
                start = t
                end = t

        edge_ranges[edge].append((start, end + timedelta(seconds=1)))

    # Convert edge ranges to show format with boolean intervals
    full_range_start = utc_time
    full_range_end = utc_time + timedelta(seconds=time_interval - 1)
    show_intervals = {}

    def format_time(t):
        return t.strftime('%Y-%m-%dT%H:%M:%SZ')

    for edge, intervals in edge_ranges.items():
        show = []
        current_start = full_range_start

        for start, end in intervals:
            if start > current_start:
                show.append({
                    "interval": f"{format_time(current_start)}/{format_time(start)}",
                    "boolean": False
                })
            show.append({
                "interval": f"{format_time(start)}/{format_time(end)}",
                "boolean": True
            })
            current_start = end

        if current_start < full_range_end:
            show.append({
                "interval": f"{format_time(current_start)}/{format_time(full_range_end)}",
                "boolean": False
            })

        show_intervals[edge] = show

    return show_intervals

# Example usage
paths = [
    ['ue-1', 'gemini-9', 'gemini-3', 'gemini-2', 'gemini-1', 'gemini-3', 'gemini-9', 'core-1']
] * 5
utc_time = datetime(2025, 1, 1, 0, 0, 0)
edge_intervals = convert_paths_to_edges(paths, utc_time, len(paths))

for edge, intervals in edge_intervals.items():
    print(f"Edge {edge}:")
    for interval in intervals:
        print(interval)
