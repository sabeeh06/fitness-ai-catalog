"""
Fitness App – CLI entry point.
Run: python main.py
"""
from fitness_app import (
    User,
    load_workouts,
    get_workouts_by_goal,
    get_goals,
    complete_workout,
)


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def main():
    """Main CLI loop for the fitness app."""
    # Load workout catalog
    workouts_db = load_workouts()
    if not workouts_db:
        print("Could not load fitness_catalog.csv. Add the file and try again.")
        return

    user = User()
    goal = None          # Current fitness goal (value)
    goal_label = None    # Display name of the goal

    print_header("Fitness App")
    print("Set your fitness goal to get personalized workout recommendations.\n")

    while True:
        print("\n--- Menu ---")
        print("1. Set fitness goal")
        print("2. Show recommended workouts")
        print("3. Complete a workout")
        print("4. View workout history")
        print("5. View rank")
        print("6. Exit")

        choice = input("\nChoice (1–6): ").strip()

        if choice == "1":
            print_header("Fitness goal")
            for num, label, value in get_goals():
                print(f"  {num}. {label}")
            sel = input("Select (1–5): ").strip()
            for num, label, value in get_goals():
                if sel == num:
                    goal = value
                    goal_label = label
                    print(f"\nGoal set to: {goal_label}")
                    break
            else:
                print("Invalid option.")

        elif choice == "2":
            if goal is None:
                print("\nSet your fitness goal first (menu option 1).")
                continue
            recs = get_workouts_by_goal(workouts_db, goal)
            print_header(f"Workouts for: {goal_label or goal}")
            if not recs:
                print("No workouts found for this goal.")
            else:
                for i, w in enumerate(recs, 1):
                    print(f"  {i}. {w['title']} ({w.get('level', '?')}) – {w.get('days_per_week', '?')} days/week")

        elif choice == "3":
            if goal is None:
                print("\nSet your fitness goal first (menu option 1).")
                continue
            recs = get_workouts_by_goal(workouts_db, goal)
            if not recs:
                print("No workouts to complete. Set a goal and check recommendations.")
                continue
            print_header("Complete a workout")
            for i, w in enumerate(recs, 1):
                print(f"  {i}. {w['title']}")
            try:
                idx = int(input("\nNumber to complete: ").strip()) - 1
                if 0 <= idx < len(recs):
                    pts = complete_workout(user, recs[idx])
                    print(f"\nWorkout completed! +{pts} points")
                else:
                    print("Invalid number.")
            except ValueError:
                print("Please enter a number.")

        elif choice == "4":
            history = user.get_history()
            print_header("Workout history")
            if not history:
                print("No workouts completed yet.")
            else:
                for w in history:
                    print(f"  • {w['title']} – {w['points']} pts ({w.get('date', '')})")

        elif choice == "5":
            info = user.view_rank()
            print_header("Your rank")
            print(f"  Tier: {info['tier']}")
            print(f"  ELO:  {info['elo']}")

        elif choice == "6":
            print("\nGoodbye!")
            break

        else:
            print("Invalid option. Enter 1–6.")


if __name__ == "__main__":
    main()
