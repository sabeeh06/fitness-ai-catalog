"""
Fitness app core: user, rank, workout catalog, and recommendations.
"""
import csv
import datetime
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# User & Rank
# ---------------------------------------------------------------------------

APP_DATA_FILE = "fitness_app_data.json"


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

    def to_dict(self):
        return {"workouts": list(self.workouts), "rank": self.rank.to_dict()}

    @staticmethod
    def from_dict(data):
        u = User()
        u.workouts = list(data.get("workouts", []))
        u.rank = Rank.from_dict(data.get("rank", {}))
        return u


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

    def to_dict(self):
        return {"elo": self.elo, "tier": self.tier}

    @staticmethod
    def from_dict(data):
        r = Rank()
        try:
            r.elo = int(data.get("elo", 0))
        except (TypeError, ValueError):
            r.elo = 0
        r._update_tier()
        if isinstance(data.get("tier"), str) and data.get("tier"):
            # Tier is derived from ELO, but keep for forward-compat.
            r.tier = data["tier"]
        return r


class Friend:
    def __init__(self, name, elo=0):
        self.name = (name or "").strip()
        self.rank = Rank()
        self.rank.elo = int(elo) if str(elo).strip() else 0
        self.rank._update_tier()

    def to_dict(self):
        return {"name": self.name, "rank": self.rank.to_dict()}

    @staticmethod
    def from_dict(data):
        name = (data.get("name") or "").strip()
        elo = (data.get("rank") or {}).get("elo", 0)
        return Friend(name=name, elo=elo)


class AppState:
    def __init__(self, user=None, friends=None):
        self.user = user or User()
        self.friends = friends or []

    def to_dict(self):
        return {
            "user": self.user.to_dict(),
            "friends": [f.to_dict() for f in self.friends],
        }

    @staticmethod
    def from_dict(data):
        user = User.from_dict(data.get("user", {}))
        friends = []
        for f in data.get("friends", []):
            try:
                friend = Friend.from_dict(f)
                if friend.name:
                    friends.append(friend)
            except Exception:
                continue
        return AppState(user=user, friends=friends)


def _data_path(filename=APP_DATA_FILE):
    return Path(__file__).parent / filename


def load_state(filename=APP_DATA_FILE):
    path = _data_path(filename)
    if not path.exists():
        return AppState()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AppState.from_dict(data if isinstance(data, dict) else {})
    except Exception:
        return AppState()


def save_state(state, filename=APP_DATA_FILE):
    path = _data_path(filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, indent=2)


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
