from database import load_catalog, save_catalog
from backend import add_item, edit_item, find_item
from frontend import (
    show_menu,
    display_items,
    display_item_details,
    get_user_choice,
    get_item_id
)

def main():
    filename = "fitness_catalog.csv"
    items = load_catalog(filename)

    while True:
        show_menu()
        choice = get_user_choice()

        if choice == "1":
            display_items(items)

        elif choice == "2":
            item_id = get_item_id()
            item = find_item(items, item_id)
            if item:
                display_item_details(item)
            else:
                print("Program not found.")

        elif choice == "3":
            add_item(items)

        elif choice == "4":
            item_id = get_item_id()
            if not edit_item(items, item_id):
                print("Program not found.")

        elif choice == "5":
            save_catalog(filename, items)
            print("Changes saved. Goodbye!")
            break

        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
