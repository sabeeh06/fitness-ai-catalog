import csv
from pathlib import Path

def load_catalog(fitness_catalog):
    path = Path(__file__).parent / fitness_catalog
    with open(path, newline='', mode='r', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)

def save_catalog(fitness_catalog, items):
    path = Path(__file__).parent / fitness_catalog
    with open(path, mode='w', newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=items[0].keys() if items else [])
        writer.writeheader()
        writer.writerows(items)
