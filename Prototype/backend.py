def find_item(items, item_id):
    item_id = str(item_id).strip()
    for item in items:
        if str(item.get("id", "")).strip() == item_id:
            return item
    return None


def add_item(items):
    print("\nAdd new program")
    new_id = input("id: ").strip()
    if not new_id:
        print("id is required.")
        return
    if find_item(items, new_id):
        print("That id already exists.")
        return

    title = input("title: ").strip()
    goal = input("goal (e.g. fat loss / muscle gain): ").strip()
    level = input("level (beginner/intermediate/advanced): ").strip()
    days_per_week = input("days_per_week: ").strip()
    description = input("description: ").strip()
    equipment = input("equipment (home/gym/none): ").strip()

    items.append(
        {
            "id": new_id,
            "title": title,
            "goal": goal,
            "level": level,
            "days_per_week": days_per_week,
            "description": description,
            "equipment": equipment,
        }
    )
    print("Added.")


def edit_item(items, item_id):
    item = find_item(items, item_id)
    if not item:
        return False

    print("\nEdit program (press Enter to keep current value)")
    for key in ["title", "goal", "level", "days_per_week", "description", "equipment"]:
        cur = str(item.get(key, ""))
        new_val = input(f"{key} [{cur}]: ").strip()
        if new_val:
            item[key] = new_val

    print("Updated.")
    return True
