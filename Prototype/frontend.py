def show_menu():
    print("\n=== Fitness Catalog (Prototype) ===")
    print("1. View all programs")
    print("2. View program details")
    print("3. Add program")
    print("4. Edit program")
    print("5. Save and exit")


def display_items(items):
    if not items:
        print("\nNo programs found.")
        return
    print("\nPrograms:")
    for item in items:
        print(f"  {item.get('id', '')}. {item.get('title', '')}")


def display_item_details(item):
    print("\nProgram details")
    for k in ["id", "title", "goal", "level", "days_per_week", "equipment", "description"]:
        if k in item:
            print(f"  {k}: {item.get(k, '')}")


def get_user_choice():
    return input("\nSelect an option (1-5): ").strip()


def get_item_id():
    return input("Enter program id: ").strip()

