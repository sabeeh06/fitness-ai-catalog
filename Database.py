import csv

def load_catalog(fitness_catalog):
    with open(fitness_catalog, newline='', mode='r') as file:
        reader = csv.DictReader(file)
        return list(reader)

def save_catalog(fitness_catalog, items):
    with open(fitness_catalog, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)
