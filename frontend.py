import csv


def load_workouts(filename):
    workouts = []

    with open(filename, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            workouts.append(row)

    return workouts


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
            return "gain muscle"
        elif choice == "2":
            return "lose weight"
        elif choice == "3":
            return "maintain fitness"
        elif choice == "4":
            return "improve endurance"
        elif choice == "5":
            return "increase flexibility"
        else:
            print("Invalid selection. Please try again.")


def get_workouts_by_goal(workouts, goal):
    recommendations = []

    for workout in workouts:
        if workout["category"].lower() == goal.lower():
            recommendations.append(workout["name"])

    return recommendations


def main():
    print("🤖 Welcome to the AI Fitness Chatbot!")

    workouts_db = load_workouts("workouts.csv")
    goal = ask_fitness_goal()

    recommended_workouts = get_workouts_by_goal(workouts_db, goal)

    print(f"\nExcellent choice! Recommending workouts to {goal}:\n")

    if recommended_workouts:
        for workout in recommended_workouts:
            print(f"- {workout}")
    else:
        print("No workouts found for this goal.")


main()
