# Fitness App (Python)

Fitness app with a modern web interface (HTML/CSS), plus desktop and CLI versions.

## Recommended run method (Web / HTML GUI)

Use this version for the updated, modern, accessible interface.

### 1) Install Python

- Python **3.7+** is required.

### 2) Clone the repo

```bash
git clone https://github.com/sabeeh06/fitness-ai-catalog
cd fitness-ai-catalog
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

If `pip` does not work, try:

```bash
python -m pip install -r requirements.txt
```

### 4) Start the web app

```bash
python web_app.py
```

If `python` does not work on Windows, try:

```bash
py web_app.py
```

### 5) Open in your browser

- [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Other run options

### Desktop GUI (Tkinter)

```bash
python gui.py
```

### Command line (CLI)

```bash
python main.py
```

## Important notes

- The **new updated UI** is the browser app (`web_app.py`), not `gui.py`.
- Your progress is saved to `fitness_app_data.json`.
- If the page looks old, make sure you opened `http://127.0.0.1:5000` and hard-refresh with `Ctrl + F5`.

## Features

- **Set fitness goal** – Muscle gain, lose weight, maintain fitness, endurance, or flexibility.
- **Recommended workouts** – View programs that match your goal.
- **Complete workouts** – Log a workout and earn points (beginner 50, intermediate 100, advanced 150).
- **Workout history** – See all completed workouts.
- **Rank** – Track ELO and tier (Bronze / Silver / Gold / Platinum).

## Project layout

- `web_app.py` – Web server for the modern HTML GUI.
- `main.py` – CLI entry point and menu.
- `gui.py` – Legacy desktop GUI (Tkinter).
- `fitness_app.py` – Core logic (user, rank, catalog, recommendations).
- `fitness_catalog.csv` – Workout catalog (id, title, goal, level, days_per_week, description, equipment).
- `frontend.py` – Original one-shot rank demo (optional).
- `Prototype/` – Prototype catalog/backend code (optional).
