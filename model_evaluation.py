import os
import json
from collections import defaultdict

# Corrected directory path
DATA_DIR = "exports/performance_metrics"

# Stores total ranking points and counts per delegate
delegate_stats = defaultdict(lambda: {"total_points": 0, "count": 0})

# Stores total ranking points and counts per model
model_stats = defaultdict(lambda: {"total_points": 0, "count": 0})

# Read all JSON files from the directory
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".json"):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r") as f:
            data = json.load(f)
            for delegate, stats in data.items():
                model = stats["model_name"]
                points = stats["ranking_points"]

                # Update delegate stats
                delegate_stats[delegate]["total_points"] += points
                delegate_stats[delegate]["count"] += 1

                # Update model stats
                model_stats[model]["total_points"] += points
                model_stats[model]["count"] += 1

# Print delegate-based results
print("Ranking Points by Delegate:")
for delegate, stats in delegate_stats.items():
    avg = stats["total_points"] / stats["count"]
    print(f"{delegate}: Total = {stats['total_points']}, Average = {avg:.2f}")

print("\nRanking Points by Model:")
for model, stats in model_stats.items():
    avg = stats["total_points"] / stats["count"]
    print(f"{model}: Total = {stats['total_points']}, Average = {avg:.2f}")