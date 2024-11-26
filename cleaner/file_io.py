# cleaner/file_io.py
import csv
from pathlib import Path
import os

def save_to_csv(filepath, data, header, sort_config=None):
    """
    Save data to a CSV file.
    Sorts data based on the provided configuration.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if sort_config:
        sort_type = sort_config.get("type", "name")
        direction = sort_config.get("direction", "asc").lower() == "asc"
        if sort_type == "name":
            sorted_data = sorted(data.items(), key=lambda x: x[0], reverse=not direction)
        elif sort_type == "count":
            sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=not direction)
        else:
            sorted_data = data.items()
    else:
        sorted_data = data.items()

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for key, value in sorted_data:
            writer.writerow([key, value])
