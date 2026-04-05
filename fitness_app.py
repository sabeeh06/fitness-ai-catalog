"""
Fitness app core: user, rank, workout catalog, and recommendations.
"""
import csv
import datetime
import json
import math
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
    
    def get_rank(self):
        return self.rank


class Rank:
    def __init__(self):
        self.elo = 0
        self.tier = "Bronze"

    def update_rank(self, points):
        self.elo += points
        self._update_tier()

    def _update_tier(self):
        elo = self.elo

        if elo == 0:
            self.tier = "Unranked"
            return

        tiers = [
            ("Iron", 0, 500),
            ("Bronze", 500, 1000),
            ("Silver", 1000, 1500),
            ("Gold", 1500, 2000),
            ("Platinum", 2000, 2500),
            ("Diamond", 2500, 3000),
            ("Master", 3000, 4000),
            ("Grandmaster", 4000, float("inf")),
        ]

        divisions = ["V", "IV", "III", "II", "I"]

        for name, low, high in tiers:
            if low <= elo < high:
                if name in ["Master", "Grandmaster"]:
                    self.tier = name
                    return
                
                rank_size = high - low
                division_size = rank_size / len(divisions)

                index = int((elo - low) / division_size)
                index = min(index, len(divisions) - 1)

                self.tier = f"{name} {divisions[index]}"

    def view(self):
        return {"tier": self.tier, "elo": self.elo}

    def to_dict(self):
        return {"elo": self.elo, "tier": self.tier}
    
    def get_elo(self):
        return self.elo

    @staticmethod
    def from_dict(data):
        r = Rank()
        try:
            r.elo = int(data.get("elo", 0))
        except (TypeError, ValueError):
            r.elo = 0
        r._update_tier()
        #if isinstance(data.get("tier"), str) and data.get("tier"):
            # Tier is derived from ELO, but keep for forward-compat.
        #    r.tier = data["tier"]
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


def points_for_level(level, user):
    level = (level or "").lower()
    elo = user.get_rank().get_elo()

    #harder workouts give more points
    base_points = {"beginner" : 40, "intermediate" : 50, "advanced" : 60}.get(level, 40)
    
    #workout points decrease as elo increases, exponentially based on how hard they are
    #(eg. beginner workouts have the highest exponent)
    exponent = 2.5 - (base_points - 40) / 40
    scale = (2500 / (elo + 2500)) ** exponent

    #weight of the point decrease is smaller for harder workouts, but goes to 1 as elo increases
    weight = {"beginner" : 0.8, "intermediate" : 0.6, "advanced" : 0.4}.get(level, 0.8)
    weight_dx = (2500 / (elo + 2500)) ** 0.25
    final_weight = (weight * weight_dx)  + (1 - weight_dx)

    #dilute scale based on workout difficulty
    multiplier = (scale * final_weight) + (1 - final_weight)
    
    #the higher official rank you are, the less points you get from workouts at a flat rate
    rank_penalty = 2 * math.floor(elo / 1000) + 1 if elo >= 3000 else math.floor(elo / 500)

    #minimum points per workout, minimum is 1 for master+
    min = 1 if elo >= 3000 else 5
    final_points = max(base_points * multiplier - rank_penalty, min)

    return math.floor(final_points)


def complete_workout(user, workout):
    level = workout.get("level", "beginner")
    points = points_for_level(level, user)
    record = {
        "title": workout.get("title", "Workout"),
        "points": points,
        "date": datetime.date.today().isoformat(),
    }
    user.add_workout(record)
    return points
