import re
import csv
import sys
from tabulate import tabulate
from datetime import datetime, timedelta, date
import calendar

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
        "4. View member and progress. \n"
        "5. Delete or edit a member. \n"
        "6. Delete a chore. \n"
        "7. Edit a chore. \n"
        "8. Tick a chore. \n"
        "9. View track record. \n"
        "10. Exit. \n"
         "Enter a number: ")
        if choice == "1": 
            create_member()
        elif choice == "2": 
            create_chore()
        elif choice == "3": 
            view_chore("Chores.csv")
        elif choice == "4": 
            view_member_progress()
        elif choice == "5": 
            edit_delete_member("Members.csv")
        elif choice == "6": 
            delete_chore("Chores.csv")
        elif choice == "7": 
            edit_chore("Chores.csv")
        elif choice == "8": 
            tick_chore()
        elif choice == "9": 
            view_completion_history()
        elif choice == "10": 
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
    while True: 
        try: 
            monthly_target = int(input("Enter monthly credit target (Reference: each chore is awarded 1-10 credits): ").strip())
        except ValueError: 
            print("Credit target must be an integer. ")
            continue
        if monthly_target >= 1: 
            break
        print("Credit target must be larger than 0. ")
    with open("Members.csv","a",newline="") as file: 
        member_id = get_id("Members.csv")
        writer = csv.DictWriter(file, fieldnames=["id", "name", "total_credits", "monthly_target"])
        if file.tell() == 0: 
            writer.writeheader()
        writer.writerow({"id":member_id, "name":member, "total_credits":0, "monthly_target": monthly_target})
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
            print("Credits must be between 1-10. ")
    while True: 
        frequency = input("Recurrance frequency of the chore (None/Daily/Weekly/Monthly): ").strip().title()
        if frequency not in ["None", "Daily", "Weekly", "Monthly"]: 
            print("Please enter a valid frequency. ")
        else: 
            break
    original_day = ""
    while True: 
        try:
            due = input("Due date (YYYY-MM-DD): ").strip()
            if not due and frequency != "None": 
                print("Reccuring chores must have a due date. ")
                continue
            if not due: 
                break
            datetime.strptime(due, "%Y-%m-%d")
            original_day = datetime.strptime(due, "%Y-%m-%d").day
            break
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.") 
    while True: 
        assignee_id = ""
        assignee_name = "None"
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
                            assignee_name = f': {row["name"]}'
                            break
                    break
                else: 
                    print("Please enter a valid id. ")
    chore_id = get_id("Chores.csv")
    with open ("Chores.csv", "a", newline="") as file: 
        writer = csv.DictWriter(file, fieldnames=["id", "chore", "credits", "due","assignee","tick", "frequency", "original_day"]) # TODO: able to add few assignee
        if file.tell() ==0: 
            writer.writeheader()
        writer.writerow({"id":chore_id, "chore": chore, "credits": credits, "due": due, "assignee": f"{assignee_id}{assignee_name}", "tick": "Pending", "frequency": frequency, "original_day": original_day})
    print("\nChore successfully added. ")

def view_chore(filename): 
    today = datetime.today().date()
    with open(filename, "r", newline="") as file: 
        reader = csv.DictReader(file)
        rows = list(reader)
        if not rows: 
            print("No chores found. ")
            return
        rows = [row for row in rows if row["tick"] == "Pending"]
        for row in rows: 
            if not row["due"]: 
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
        if not rows: 
            print("No chores found. ")
            return
        print(tabulate(rows, headers="keys"))

def view_member_progress(): 
    with open("Members.csv", "r", newline="") as file: 
        reader = csv.DictReader(file)
        rows = list(reader)
        if not rows: 
            print("No member found. ")
            return
        monthly_progress = get_monthly_progress("CreditHistory.csv")
        for row in rows: 
            monthly_credits = monthly_progress.get(row["id"], 0)
            monthly_target = int(row["monthly_target"])
            row["progress"] = f"{int((monthly_credits/monthly_target)*100)} %"
        print(tabulate(rows, headers="keys")) 

def edit_delete_member(filename): 
    while True: 
        choice = input('Enter "delete" or "edit" to modify a member (or Q to undo): ').strip()
        if choice.lower() == "q": 
            print("Deletion cancelled. ")
            return
        elif choice.lower() == "delete" or choice.lower() == "edit": 
            with open(filename,"r",newline="") as file: 
                reader = csv.DictReader(file)
                fieldnames = reader.fieldnames
                rows = list(reader)
                id_list = [row["id"] for row in rows]
            if choice.lower() == "delete": 
                view_member_progress()
                delete = input("Enter a member id for removal: ").strip()
                delete = delete.zfill(3)
                if delete not in id_list: 
                    print("Member not found. ")
                    return
                while True: 
                    confirmation = input(f"Warning: Chores assigned to this member will be unassigned. \nConfirm deletion on member {delete} (Yes/No): ").lower().strip()
                    if confirmation == "no": 
                        print("Deletion cancelled. ")
                        return
                    elif confirmation == "yes": 
                        rows = [row for row in rows if row["id"] != delete]
                        with open("Chores.csv","r",newline="") as file: 
                            chore_reader = csv.DictReader(file)
                            chore_rows = list(chore_reader)
                            chore_fieldnames = chore_reader.fieldnames
                        for chore_row in chore_rows: 
                            if chore_row["assignee"].split(": ")[0] == delete: 
                                chore_row["assignee"] = "None"
                        with open("Chores.csv","w",newline="") as file: 
                            chore_writer = csv.DictWriter(file, fieldnames=chore_fieldnames)
                            chore_writer.writeheader()
                            chore_writer.writerows(chore_rows)
                        print("Member deleted. ")
                        break
                    else: 
                        print("Please enter a valid input. ")
            elif choice.lower() == "edit": 
                view_member_progress()
                edit = input("Enter a member id for edition: ").strip()
                edit = edit.zfill(3)
                if edit not in id_list: 
                    print("Member not found. ")
                    return
                while True: 
                    edited_name = input("Please enter a new name for the member. ").strip().title()
                    if edited_name: 
                        break
                    print("Member cannot be empty. ")
                for row in rows: 
                    if row["id"] == edit: 
                        row["name"] = edited_name
                        break
                print("Member edited. ")
            with open(filename, "w", newline="") as file: 
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            return
        else: 
            print("Please enter a valid input (delete/edit). ")

def delete_chore(filename): 
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
            part = input("Choose a section to edit (chore/credits/due/assignee/frequency): ").lower().strip()
            if part in ["chore", "chores", "credit", "credits", "due", "due date", "assignee", "frequency"]: 
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
            view_member_progress()
            while True: 
                change = input("Enter a member's id (Enter if want to unassign): ").strip()
                if change == "":
                    member_name_change = "None"
                    break
                change = change.zfill(3)
                with open("Members.csv","r",newline="") as file: 
                    reader = csv.DictReader(file)
                    members = list(reader)
                    member_id_list = [member["id"] for member in members]
                if change in member_id_list: 
                    for member in members: 
                        if member["id"] == change: 
                            member_name_change = f": {member['name']}"
                            break
                    break
                else: 
                    print("Member id doesn't exists. ")
            for row in rows: 
                if row["id"] == edit: 
                    row["assignee"] = f"{change}{member_name_change}"
                    break
        elif part == "frequency": 
            for row in rows: 
                if row["id"] == edit:  
                    while True: 
                        change = input("Enter a new frequency (None/Daily/Weekly/Monthly): ").strip().title()
                        if change not in ["None", "Daily", "Weekly", "Monthly"]: 
                            print("Please enter a valid frequency")
                            continue
                        if change != "None" and row["due"] == "": 
                            print("Recurring chores must have due date. ")
                            while True: 
                                try: 
                                    due = input("Please enter a due date (YYYY-MM-DD) (Or Q to cancel). ").strip()
                                    if due.lower() == "q": 
                                        return
                                    parsed_due = datetime.strptime(due, "%Y-%m-%d")
                                    original_day = str(parsed_due.day)
                                    row["due"] = due
                                    row["original_day"] = original_day
                                    break
                                except ValueError: 
                                    print("Invalid date. Use YYYY-MM-DD.")
                        row["frequency"] = change
                        break
        else: 
            while True: 
                try:
                    change = input("Enter a new due date: ").strip()
                    if not change: 
                        for row in rows: 
                            if row["id"] == edit: 
                                if row["frequency"] != "None": 
                                    print("Cannot delete due date for reccuring chores. ")
                                    return
                        break
                    datetime.strptime(change, "%Y-%m-%d")
                    break
                except ValueError:
                    print("Invalid date. Use YYYY-MM-DD.")
            for row in rows: 
                if row["id"] == edit: 
                    row["due"] = change
                    row["original_day"] = datetime.strptime(change, "%Y-%m-%d").day if change else ""
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
                chore_name = chore_row["chore"]
                assignee = chore_row["assignee"].split(":")[0]
                if assignee == "None": 
                    while True: 
                        view_member_progress()
                        assignee = input("Enter the member's id of whom the credits are given to: ").strip()
                        if assignee == "":
                            print("Please enter a member id.")
                            continue
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
                new_chore = None
                if chore_row["frequency"] != "None": 
                    new_id = get_id("Chores.csv")
                    current_due = datetime.strptime(chore_row["due"], "%Y-%m-%d").date()
                    if chore_row["frequency"] == "Daily": 
                        new_due = current_due + timedelta(days=1)
                    elif chore_row["frequency"] == "Weekly": 
                        new_due = current_due + timedelta(days=7)
                    else: 
                        year = current_due.year
                        month = current_due.month + 1
                        if month > 12: 
                            year += 1
                            month = 1
                        total_days_of_month = calendar.monthrange(year, month)[1]
                        day = min(int(chore_row["original_day"]), total_days_of_month)
                        new_due = current_due.replace(year=year, month=month, day=day)
                    new_due = new_due.strftime("%Y-%m-%d")
                    new_chore = {"id":new_id,"chore":chore_row["chore"],"credits":chore_row["credits"],"due":new_due,"assignee":chore_row["assignee"],"tick":"Pending","frequency":chore_row["frequency"], "original_day": chore_row["original_day"]}
                break
    with open("Members.csv","r",newline="") as file: 
        member_reader = csv.DictReader(file)
        member_rows = list(member_reader)
        members_fieldnames = member_reader.fieldnames
    for member_row in member_rows: 
        if assignee == member_row["id"]: 
            assignee_name = member_row["name"]
            member_row["total_credits"]   = credits + int(member_row["total_credits"])
            break
    with open("Chores.csv","w",newline="") as file: 
        chore_writer = csv.DictWriter(file, fieldnames=chore_fieldnames)
        chore_writer.writeheader()
        if new_chore is not None: 
            chore_rows.append(new_chore)
        chore_writer.writerows(chore_rows)
    with open("Members.csv","w",newline="") as file: 
        member_writer = csv.DictWriter(file, fieldnames=members_fieldnames)
        member_writer.writeheader()
        member_writer.writerows(member_rows)
    with open("CreditHistory.csv","a",newline="") as file: 
        history_writer = csv.DictWriter(file, fieldnames=["member", "chore", "completion_date", "credits"])
        if file.tell() == 0: 
            history_writer.writeheader()
        history_writer.writerow({"member": f"{assignee}: {assignee_name}", "chore": f"{tick}: {chore_name}", "completion_date": date.today(), "credits": credits})
    print("Chore ticked. ")

def get_monthly_progress(filename): 
    current_month = date.today().strftime("%Y-%m")
    with open(filename,"a",newline="") as file: 
        history_writer = csv.DictWriter(file, fieldnames=["member", "chore", "completion_date", "credits"])
        if file.tell() == 0: 
            history_writer.writeheader()
    with open(filename,"r",newline="") as file: 
        history_reader = csv.DictReader(file)
        rows = list(history_reader)
    monthly_progress = {}
    for row in rows: 
        if row["completion_date"][:7] == current_month: 
            member_id = row["member"].split(": ")[0]
            credits = int(row["credits"])
            if member_id not in monthly_progress: 
                monthly_progress[member_id] = 0
            monthly_progress[member_id] += credits
    return monthly_progress

def view_completion_history(): 
    with open("CreditHistory.csv", "r", newline="") as file: 
        history_reader = csv.DictReader(file)
        history_rows = list(history_reader)
        if not history_rows: 
            print("No history found. ")
            return
    print(tabulate(history_rows, headers="keys")) 

if __name__ == "__main__":
    main()