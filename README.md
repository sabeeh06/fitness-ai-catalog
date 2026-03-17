# Fitness App (Python)

A command-line fitness app: set a goal, get workout recommendations, log workouts, and track your rank (Bronze → Silver → Gold → Platinum).

## Setup

1. Install **Python 3.7+** on your machine.
2. Clone the repo:  
   `git clone https://github.com/sabeeh06/fitness-ai-catalog`
3. Ensure `fitness_catalog.csv` is in the same folder as `main.py` and `fitness_app.py`.

## Run

From the project folder:

```bash
python main.py
```

Or, if you use `python3`:

```bash
python3 main.py
```

## Run (GUI)

From the project folder:

```bash
python gui.py
```

## Features

- **Set fitness goal** – Muscle gain, lose weight, maintain fitness, endurance, or flexibility.
- **Recommended workouts** – View programs that match your goal.
- **Complete workouts** – Log a workout and earn points (beginner 50, intermediate 100, advanced 150).
- **Workout history** – See all completed workouts.
- **Rank** – Track ELO and tier (Bronze / Silver / Gold / Platinum).

## Project layout

- `main.py` – Entry point and menu.
- `fitness_app.py` – Core logic (user, rank, catalog, recommendations).
- `fitness_catalog.csv` – Workout catalog (id, title, goal, level, days_per_week, description, equipment).
- `frontend.py` – Original one-shot rank demo (optional).
- `Prototype/` – Prototype catalog/backend code (optional).
