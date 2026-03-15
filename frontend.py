import csv
import datetime


# USER CLASS

class User:
    def __init__(self):
        self.curDate = datetime.date.today()
        self.workouts = []
        self.rank = Rank()

    def addWorkout(self, workout):
        self.workouts.append(workout)
        self.rank.updateRank(workout["points"])

    def displayHistory(self):
        if not self.workouts:
            print("No workouts completed yet.")
            return

        print("\nWorkout History")
        for w in self.workouts:
            print(f"{w['title']} - {w['points']} points")

    def viewRank(self):
        self.rank.view()


# RANK SYSTEM

class Rank:

    def __init__(self):
        self.elo = 0
        self.tier = "Bronze"
        self.timeSinceLastWorkout = 0

    def updateRank(self, points):
        self.elo += points
        self.updateTier()

    def updateTier(self):

        if self.elo < 100:
            self.tier = "Bronze"
        elif self.elo < 250:
            self.tier = "Silver"
        elif self.elo < 500:
            self.tier = "Gold"
        else:
            self.tier = "Platinum"

    def view(self):
        print("\n===== YOUR RANK =====")
        print(f"Tier: {self.tier}")
        print(f"ELO: {self.elo}")
        print("=====================")



# LOAD WORKOUT DATABASE

def load_workouts(filename):

    workouts = []

    with open(filename, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            workouts.append(row)

    return workouts



# ASK FITNESS GOAL

def ask_fitness_goal():

    while True:

        print("\nWhat is your main fitness goal?")
        print("1. Gain muscle")
        print("2. Lose weight")
        print("3. Maintain fitness")
        print("4. Improve endurance")
        print("5. Increase flexibility")

        choice = input("Select an option (1-5): ")

        if choice == "1":
            return "muscle gain"
        elif choice == "2":
            return "fat loss"
        elif choice == "3":
            return "strength"
        elif choice == "4":
            return "endurance"
        elif choice == "5":
            return "mobility"
        else:
            print("Invalid selection.")



# GET WORKOUTS BY GOAL

def get_workouts_by_goal(workouts, goal):

    recommendations = []

    for workout in workouts:
        if workout["goal"].lower() == goal.lower():
            recommendations.append(workout)

    return recommendations



# DISPLAY RECOMMENDATIONS

def display_recommendations(recommendations):

    if not recommendations:
        print("No workouts found.")
        return

    print("\nRecommended Programs:\n")

    for i, workout in enumerate(recommendations):

        print(f"{i+1}. {workout['title']} ({workout['level']})")



# COMPLETE WORKOUT

def complete_workout(user, workout):

    # simple point system
    level = workout["level"]

    if level == "beginner":
        points = 50
    elif level == "intermediate":
        points = 100
    else:
        points = 150

    workout_record = {
        "title": workout["title"],
        "points": points
    }

    user.addWorkout(workout_record)

    print(f"\nWorkout completed! +{points} points")



# USER INTERFACE

def main():

    print("Welcome to the Fitness Rank System!")

    workouts_db = load_workouts("fitness_catalog.csv")

    user = User()

    goal = ask_fitness_goal()

    recommendations = get_workouts_by_goal(workouts_db, goal)

    display_recommendations(recommendations)

    if recommendations:

        choice = int(input("\nSelect workout to complete: ")) - 1

        if 0 <= choice < len(recommendations):

            complete_workout(user, recommendations[choice])

    user.viewRank()

    user.displayHistory()


main()
