import csv
from pathlib import Path
from typing import List, Dict, Optional


DEFAULT_CSV = Path(__file__).parent / "catalog.csv"


def load_workouts(filename: Optional[Path] = None) -> List[Dict[str, str]]:
    """Load workouts from a CSV file and return a list of dicts.

    If the file does not exist or cannot be read, a helpful error is raised.
    """
    path = Path(filename) if filename else DEFAULT_CSV

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    workouts: List[Dict[str, str]] = []
    with path.open(newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Normalize keys to lowercase for predictable access
            workouts.append({k.strip().lower(): (v.strip() if v is not None else "") for k, v in row.items()})

    return workouts


def ask_fitness_goal() -> str:
    """Prompt user for a fitness goal and return a normalized goal string.

    The returned string should match values present in the CSV `goal` column.
    """
    choices = {
        "1": "muscle gain",
        "2": "fat loss",
        "3": "maintain fitness",
        "4": "endurance",
        "5": "flexibility",
    }

    prompt_lines = [
        "\nWhat is your main fitness goal?",
        "1. Gain muscle",
        "2. Lose weight",
        "3. Maintain fitness",
        "4. Improve endurance",
        "5. Increase flexibility",
    ]

    while True:
        for line in prompt_lines:
            print(line)
        choice = input("Select an option (1-5): ").strip()
        if choice in choices:
            return choices[choice]
        # allow entering a free-text goal as well
        if choice:
            return choice.lower()
        print("Invalid selection. Please try again.")


def get_workouts_by_goal(workouts: List[Dict[str, str]], goal: str) -> List[Dict[str, str]]:
    """Return a list of workout dicts whose `goal` matches the requested goal.

    Matching is case-insensitive and matches common synonyms (e.g. "lose weight" -> "fat loss").
    """
    synonyms = {
        "lose weight": "fat loss",
        "gain muscle": "muscle gain",
        "improve endurance": "endurance",
        "increase flexibility": "flexibility",
    }

    normalized_goal = synonyms.get(goal.lower(), goal.lower())
    matches: List[Dict[str, str]] = []
    for w in workouts:
        if w.get("goal", "").lower() == normalized_goal:
            matches.append(w)
    return matches


def print_workout_summary(workout: Dict[str, str]) -> None:
    """Print a readable summary for a single workout entry."""
    title = workout.get("title", "Untitled")
    level = workout.get("level", "")
    days = workout.get("days_per_week", "")
    equipment = workout.get("equipment", "")
    desc = workout.get("description", "").strip()

    print(f"- {title} ({level}, {days} days/week) — equipment: {equipment}")
    if desc:
        print(f"  {desc}")


def main() -> None:
    print("🤖 Welcome to the AI Fitness Chatbot!")

    try:
        workouts_db = load_workouts()
    except FileNotFoundError as exc:
        print(exc)
        return

    goal = ask_fitness_goal()
    recommended_workouts = get_workouts_by_goal(workouts_db, goal)

    print(f"\nExcellent choice! Recommending workouts for: {goal}\n")

    if recommended_workouts:
        for workout in recommended_workouts:
            print_workout_summary(workout)
    else:
        print("No workouts found for this goal.")


if __name__ == "__main__":
    main()
