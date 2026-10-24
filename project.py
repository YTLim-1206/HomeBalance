import re
import csv
import sys
from tabulate import tabulate
from datetime import datetime

def main(): 
    while True: 
        print(
        "\n=============\n" 
        " HOMEBALANCE \n" 
        "=============\n")
        choice = input(
        "1. Create a chore. \n" 
        "2. View chore list. \n" 
        "3. Delete a chore. \n"
        "4. Edit a chore. \n"
        "5. Exit. \n"
         "Enter a number: ")
        if choice == "1": 
            create_chore()
        elif choice == "2": 
            view_chore("Chores.csv")
        elif choice == "3": 
            remove_chore("Chores.csv")
        elif choice == "4": 
            edit_chore("Chores.csv")
        elif choice == "5": 
            sys.exit("System closed. ")
        else: 
            print("Please enter a valid number. ")

def get_id(filename): 
    try: 
        with open (filename, "r", newline="") as file: 
            reader = csv.DictReader(file)
            for row in reader: 
                idx = [int(row["id"])]
            return f"{max(idx, default=0)+1 :03d}"
    except FileNotFoundError: 
        return 1

def create_chore(): 
    while True: 
        chore = input("Chore name: ").strip().title()
        if chore: 
            break
        else: 
            print("Chore cannot be empty. ")
    while True: 
        try: 
            credits = int(input("credits (/10): "))
        except ValueError: 
            print("Invalid credits format. ")
            continue
        if 1 <= credits <= 10: 
            break
        else: 
            print("credits must be between 1-10. ")
    while True: 
        try:
            due = input("Due date (YYYY-MM-DD): ").strip()
            if not due: 
                break
            datetime.strptime(due, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.") 
    chore_id = get_id("Chores.csv")
    with open ("Chores.csv", "a", newline="") as file: 
        writer = csv.DictWriter(file, fieldnames=["id", "chore", "credits", "due"])
        if file.tell() ==0: 
            writer.writeheader()
        writer.writerow({"id":chore_id, "chore": chore, "credits": credits, "due": due})
    print("\nChore successfuly added")

def view_chore(filename): 
    with open(filename, "r", newline="") as file: 
        reader = csv.reader(file)
        headers = next(reader)
        if headers is None: 
            print("No chores found. ")
            return
        print(tabulate(reader, headers=headers))

def remove_chore(filename): 
    view_chore(filename)
    remove = input("Enter a chore id for removal (or Q to undo): ").strip()
    if remove.lower() == "q": 
        print("Deletion cancelled. ")
        return
    remove = remove.zfill(3)

    with open(filename, "r", newline="") as file: 
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        rows = list(reader)

        id_list = [row["id"] for row in rows]
        if remove not in id_list: 
            print("Chore not found. ")
            return
        while True: 
            confirmation = input(f"Confirm deletion on chore {remove} (Yes/No): ").lower().strip()
            if confirmation == "no": 
                print("Deletion cancelled. ")
                return
            elif confirmation == "yes": 
                rows = [row for row in rows if row["id"] != remove]
                break
            else: 
                print("Please enter a valid input. ")
        with open(filename, "w", newline="") as file: 
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print("Chore deleted. ")

def edit_chore(filename): 
    view_chore(filename)
    edit = input("Enter a chore id for edition (or Q to undo): ").strip()
    if edit.lower() == "q": 
        print("edition cancelled. ")
        return
    edit = edit.zfill(3)

    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames
        id_list = [row["id"] for row in rows]
        if edit not in id_list: 
            print("Chore not found. ")
            return
        while True: 
            part = input("Choose a section to edit (chore/credits/due): ").lower().strip()
            if part in ["chore", "chores", "credit", "credits", "due", "due date"]: 
                break
            else: 
                print("Please enter a valid section. ")
        if part == "chore" or part == "chores": 
            while True: 
                change = input("Enter a new chore name: ").title().strip()
                if change: 
                    break
                else: 
                    print("Chore cannot be empty. ")
            for row in rows: 
                if row["id"] == edit: 
                    row["chore"] = change
                    break
        elif part == "credit" or part == "credits": 
            while True: 
                try: 
                    change = int(input("Enter a new credit (/10): ").strip())
                except ValueError: 
                    print("Invalid credits format. ")
                    continue
                if 1 <= change <= 10: 
                    break
                else: 
                    print("credits must be between 1-10. ")
            for row in rows: 
                if row["id"] == edit: 
                    row["credits"] = str(change)
                    break
        else: 
            while True: 
                try:
                    change = input("Enter a new due date: ").strip()
                    if not change: 
                        break
                    datetime.strptime(change, "%Y-%m-%d")
                    break
                except ValueError:
                    print("Invalid date. Use YYYY-MM-DD.")
            for row in rows: 
                if row["id"] == edit: 
                    row["due"] = change
                    break
    with open(filename, "w", newline="") as file: 
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Chore {edit} updated successfully. ")

if __name__ == "__main__":
    main()