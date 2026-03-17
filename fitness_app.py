"""
Fitness app core: user, rank, workout catalog, and recommendations.
"""
import csv
import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# User & Rank
# ---------------------------------------------------------------------------

class User:
    def __init__(self):
        self.workouts = []
        self.rank = Rank()

    def add_workout(self, workout):
        self.workouts.append(workout)
        self.rank.update_rank(workout["points"])

    def get_history(self):
        return self.workouts

    def view_rank(self):
        return self.rank.view()


class Rank:
    def __init__(self):
        self.elo = 0
        self.tier = "Bronze"

    def update_rank(self, points):
        self.elo += points
        self._update_tier()

    def _update_tier(self):
        if self.elo < 100:
            self.tier = "Bronze"
        elif self.elo < 250:
            self.tier = "Silver"
        elif self.elo < 500:
            self.tier = "Gold"
        else:
            self.tier = "Platinum"

    def view(self):
        return {"tier": self.tier, "elo": self.elo}


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

def load_workouts(filename="fitness_catalog.csv"):
    path = Path(__file__).parent / filename
    if not path.exists():
        return []
    workouts = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Strip any extra key from trailing comma in header
        fieldnames = [k.strip() for k in reader.fieldnames if k.strip()]
        for row in reader:
            row = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items() if k.strip()}
            if row.get("id") and row.get("title"):
                workouts.append(row)
    return workouts


def get_workouts_by_goal(workouts, goal):
    if not goal:
        return []
    goal_lower = goal.lower().strip()
    return [w for w in workouts if w.get("goal", "").lower().strip() == goal_lower]


def get_goals():
    return [
        ("1", "Gain muscle", "muscle gain"),
        ("2", "Lose weight", "fat loss"),
        ("3", "Maintain fitness", "strength"),
        ("4", "Improve endurance", "endurance"),
        ("5", "Increase flexibility", "mobility"),
    ]


def points_for_level(level):
    level = (level or "").lower()
    if level == "beginner":
        return 50
    if level == "intermediate":
        return 100
    if level == "advanced":
        return 150
    return 50


def complete_workout(user, workout):
    level = workout.get("level", "beginner")
    points = points_for_level(level)
    record = {
        "title": workout.get("title", "Workout"),
        "points": points,
        "date": datetime.date.today().isoformat(),
    }
    user.add_workout(record)
    return points
