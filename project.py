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
        "1. Add member. \n"
        "2. Create a chore. \n" 
        "3. View chore list. \n" 
        "4. Delete a chore. \n"
        "5. Edit a chore. \n"
        "6. Tick a chore. \n"
        "7. Exit. \n"
         "Enter a number: ")
        if choice == "1": 
            create_member()
        elif choice == "2": 
            create_chore()
        elif choice == "3": 
            view_chore("Chores.csv")
        elif choice == "4": 
            remove_chore("Chores.csv")
        elif choice == "5": 
            edit_chore("Chores.csv")
        elif choice == "6": 
            tick_chore()
        elif choice == "7": 
            sys.exit("System closed. ")
        else: 
            print("Please enter a valid number. ")

def get_id(filename): 
    try: 
        with open (filename, "r", newline="") as file: 
            reader = csv.DictReader(file)
            max_id = 0
            for row in reader: 
                max_id = max(max_id, int(row["id"]))
            return f"{max_id +1 :03d}"
    except FileNotFoundError: 
        return "001"
    
def create_member(): 
    while True: 
        member = input("Name: ").strip().title()
        if member: 
            break
        print("Member cannot be empty. ")
    with open("Members.csv","a",newline="") as file: 
        member_id = get_id("Members.csv")
        writer = csv.DictWriter(file, fieldnames=["id", "name", "total_credits"])
        if file.tell() == 0: 
            writer.writeheader()
        writer.writerow({"id":member_id, "name":member, "total_credits":0})
    print("\nMember successfully added. ")

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
    while True: 
        assignee_id = ""
        assignee_name = ""
        assignee_id = input("Assignee (member id): ")
        if not assignee_id: 
            break
        else: 
            assignee_id = assignee_id.zfill(3)
            with open("Members.csv","r",newline="") as file: 
                reader = csv.DictReader(file)
                rows = list(reader)
                member_id_list = [row["id"] for row in rows]
                if assignee_id in member_id_list: 
                    for row in rows: 
                        if assignee_id == row["id"]: 
                            assignee_name = row["name"]
                            break
                    break
                else: 
                    print("Please enter a valid id. ")
    chore_id = get_id("Chores.csv")
    with open ("Chores.csv", "a", newline="") as file: 
        writer = csv.DictWriter(file, fieldnames=["id", "chore", "credits", "due","assignee","tick"]) # TODO: able to add few assignee
        if file.tell() ==0: 
            writer.writeheader()
        writer.writerow({"id":chore_id, "chore": chore, "credits": credits, "due": due, "assignee":f"{assignee_id}: {assignee_name}", "tick": "Pending"})
    print("\nChore successfuly added")

def view_chore(filename): 
    today = datetime.today().date()
    with open(filename, "r", newline="") as file: 
        reader = csv.DictReader(file)
        rows = list(reader)
        if not rows: 
            print("No chores found. ")
            return
        for row in rows: 
            if row["tick"] == "Completed": 
                status = ""
            elif not row["due"]: 
                status = "no due date"
            else: 
                due_date = datetime.strptime(row["due"], "%Y-%m-%d").date()
                if today < due_date: 
                    status = "Upcoming"
                elif today == due_date: 
                    status = "Due today"
                else: 
                    status = "Overdue"
            row["status"] = status
        print(tabulate(rows, headers="keys"))

def view_member(): 
    with open("Members.csv", "r", newline="") as file: 
        reader = csv.DictReader(file)
        rows = list(reader)
        if not rows: 
            print("No member found. ")
            return
        print(tabulate(rows, headers="keys"))

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
            part = input("Choose a section to edit (chore/credits/due/assignee): ").lower().strip()
            if part in ["chore", "chores", "credit", "credits", "due", "due date", "assignee"]: 
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
        elif part == "assignee": 
            view_member()
            while True: 
                change = input("Enter a member's id: ").strip()
                change = change.zfill(3)
                with open("Members.csv","r",newline="") as file: 
                    reader = csv.DictReader(file)
                    members = list(reader)
                    member_id_list = [member["id"] for member in members]
                    if change in member_id_list: 
                        for member in members: 
                            if member["id"] == change: 
                                member_name_change = member["name"]
                                break
                        break
                    else: 
                        print("Member id doesn't exists. ")
            for row in rows: 
                if row["id"] == edit: 
                    row["assignee"] = f"{change}: {member_name_change}"
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

def tick_chore(): 
    view_chore("Chores.csv")
    tick = input("Enter a chore id for checking (or Q to undo): ").strip()
    if tick.lower() == "q": 
        print("Checking cancelled. ")
        return
    tick = tick.zfill(3)
    with open("Chores.csv","r",newline="") as file: 
        chore_reader = csv.DictReader(file)
        chore_rows = list(chore_reader)
        chore_fieldnames = chore_reader.fieldnames
        chore_id_list = [chore_row["id"] for chore_row in chore_rows]
        if tick not in chore_id_list: 
            print("Chore not found. ")
            return
        for chore_row in chore_rows: 
            if tick == chore_row["id"]: 
                if chore_row["tick"] != "Pending": 
                    print("Chore already completed. ")
                    return
                credits = int(chore_row["credits"])
                assignee = chore_row["assignee"].split(":")[0]
                if assignee == "": 
                    while True: 
                        view_member()
                        assignee = input("Enter the member's id of whom the credits are given to: ").strip()
                        assignee = assignee.zfill(3)
                        with open("Members.csv","r",newline="") as file: 
                            member_reader = csv.DictReader(file)
                            member_rows = list(member_reader)
                            member_id_list = [member_row["id"] for member_row in member_rows]
                            if assignee not in member_id_list: 
                                print("Member not found. ")
                            else: 
                                for member_row in member_rows: 
                                    if assignee == member_row["id"]: 
                                        assignee_name = member_row["name"]
                                        break
                                chore_row["assignee"] = f"{assignee}: {assignee_name}"
                                break
                chore_row["tick"] = "Completed"
                break
        with open("Members.csv","r",newline="") as file: 
            member_reader = csv.DictReader(file)
            member_rows = list(member_reader)
            members_fieldnames = member_reader.fieldnames
            for member_row in member_rows: 
                if assignee == member_row["id"]: 
                    member_row["total_credits"]   = credits + int(member_row["total_credits"])
                    break
        with open("Chores.csv","w",newline="") as file: 
            chore_writer = csv.DictWriter(file, fieldnames=chore_fieldnames)
            chore_writer.writeheader()
            chore_writer.writerows(chore_rows)
        with open("Members.csv","w",newline="") as file: 
            member_writer = csv.DictWriter(file, fieldnames=members_fieldnames)
            member_writer.writeheader()
            member_writer.writerows(member_rows)
        print("Chore ticked. ")
            
if __name__ == "__main__":
    main()