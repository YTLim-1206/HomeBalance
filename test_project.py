import pytest
import csv
from datetime import datetime, timedelta
from project import get_monthly_progress, get_id, create_member, create_chore, view_chore, view_member_progress, edit_delete_member, delete_chore, edit_chore, tick_chore, view_completion_history

def test_get_monthly_progress(tmp_path): 
    filename = tmp_path / "CreditHistory.csv"
    today = datetime.today()
    previous_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
    today = today.strftime("%Y-%m-%d")
    with open(filename,"w",newline="") as file: 
        writer = csv.DictWriter(file, fieldnames=["member", "chore", "completion_date", "credits"])
        writer.writeheader()
        writer.writerow({
            "member": "001: Patrick", 
            "chore": "001: Floor", 
            "completion_date": today, 
            "credits": "5"
        })
        writer.writerow({
            "member": "001: Patrick", 
            "chore": "002: Dishes", 
            "completion_date": today, 
            "credits": "2"
        })
        writer.writerow({
            "member": "002: Teresa", 
            "chore": "003: Windows", 
            "completion_date": today, 
            "credits": "8"
        })
        writer.writerow({
            "member": "003: Lisbon", 
            "chore": "001: Floor", 
            "completion_date": previous_month, 
            "credits": "5"
        })
    assert get_monthly_progress(filename) == {"001": 7, "002": 8}

def test_get_id(tmp_path): 
    filename = tmp_path / "Members.csv"
    assert get_id(filename) == "001"
    filename.write_text(
        "id,name,total_credits,monthly_target\n"
        "001,John,10,30\n"
        "002,Mary,15,40\n"
    )
    assert get_id(filename) == "003"
    filename.write_text(
        "id,name,total_credits,monthly_target\n"
        "008,John,10,30\n"
        "009,Mary,15,40\n"
    )
    assert get_id(filename) == "010"

def test_create_member(tmp_path, monkeypatch, capsys): 
    monkeypatch.chdir(tmp_path)

    answers = iter(["", "John", "try", "-10", "10"])
    monkeypatch.setattr("builtins.input", lambda _:next(answers))
    create_member() 
    captured = capsys.readouterr()

    assert "Member cannot be empty. " in captured.out
    assert "Credit target must be an integer. " in captured.out
    assert "Credit target must be larger than 0. " in captured.out
    assert "Member successfully added. " in captured.out

    filename = tmp_path / "Members.csv"
    assert filename.exists()

    with open(filename,"r",newline="") as file: 
        reader = csv.DictReader(file)
        rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["id"] == "001"
    assert rows[0]["name"] == "John"
    assert rows[0]["total_credits"] == "0"
    assert rows[0]["monthly_target"] == "10"

def test_create_chore(tmp_path, monkeypatch,capsys): 
    monkeypatch.chdir(tmp_path)

    with open("Members.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "name", "total_credits", "monthly_target"])
        writer.writeheader()
        writer.writerow({
            "id": "001",
            "name": "Patrick",
            "total_credits": "0",
            "monthly_target": "30"
        })

    today = today = datetime.today().strftime("%Y-%m-%d")
    answers = iter(["", "Dishes", 
                    "", "12", "3", 
                    "try", "Daily", 
                    "", today, 
                    "100", "1"])
    monkeypatch.setattr("builtins.input", lambda _ :next(answers))
    create_chore()
    capture = capsys.readouterr()

    assert "Chore cannot be empty. " in capture.out
    assert "Invalid credits format. " in capture.out
    assert "Credits must be between 1-10. " in capture.out
    assert "Please enter a valid frequency. " in capture.out
    assert "Reccuring chores must have a due date. " in capture.out
    assert "Please enter a valid id. " in capture.out
    assert "Chore successfully added. " in capture.out

    filename = tmp_path / "Chores.csv"
    assert filename.exists()
    with open(filename,"r",newline="") as file: 
        reader = csv.DictReader(file)
        rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["id"] == "001"
    assert rows[0]["chore"] == "Dishes"
    assert rows[0]["credits"] == "3"
    assert rows[0]["due"] == today
    assert rows[0]["assignee"] == "001: Patrick"
    assert rows[0]["tick"] == "Pending"
    assert rows[0]["frequency"] == "Daily"
    assert rows[0]["original_day"] == str(datetime.strptime(today, "%Y-%m-%d").day)

def test_view_chore(tmp_path, capsys): 
    filename = tmp_path / "Chores.csv"
    today = datetime.today().strftime("%Y-%m-%d")

    filename.write_text("")
    view_chore(filename)
    captured = capsys.readouterr()
    assert "No chores found. " in captured.out

    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "chore", "credits", "due", "assignee", "tick", "frequency", "original_day"])
        writer.writeheader()
        writer.writerow({
            "id": "001",
            "chore": "Dishes",
            "credits": "3",
            "due": "2026-11-05", 
            "assignee": "001: John", 
            "tick": "Completed", 
            "frequency": "None", 
            "original_day": "5"
        })
        writer.writerow({
            "id": "002",
            "chore": "Laundry",
            "credits": "5",
            "due": today, 
            "assignee": "001: John", 
            "tick": "Pending", 
            "frequency": "Monthly", 
            "original_day": "1"
        })
        writer.writerow({
            "id": "003",
            "chore": "Mopping",
            "credits": "7",
            "due": "2026-11-04", 
            "assignee": "001: John", 
            "tick": "Pending", 
            "frequency": "None", 
            "original_day": "4"
        })

    view_chore(filename)
    captured = capsys.readouterr()
    assert "Dishes" not in captured.out
    assert "Laundry" in captured.out
    assert "Mopping" in captured.out
    assert "chore" in captured.out
    assert "status" in captured.out
    assert "Overdue" in captured.out
    assert "Due today" in captured.out

def test_view_member_progress(tmp_path, capsys, monkeypatch): 
    monkeypatch.chdir(tmp_path)
    filename = tmp_path / "Members.csv"
    filename_2 = tmp_path / "CreditHistory.csv"

    filename.write_text("id,name,total_credits,monthly_target\n")
    view_member_progress()
    captured = capsys.readouterr()
    assert "No member found. " in captured.out

    filename_2.write_text("member,chore,completion_date,credits\n"
                        "001: Patrick,Dishes,2026-11-05,7\n"
                        "002: Jane,Laundry,2026-11-05,0\n"
                        "003: Lisbon,Mopping,2026-11-05,9\n")
    filename.write_text("id,name,total_credits,monthly_target\n"
                        "001,Patrick,7,14\n"
                        "002,Jane,0,9\n"
                        "003,Lisbon,9,10\n")
    view_member_progress()
    captured = capsys.readouterr()
    assert "progress" in captured.out
    assert "50 %" in captured.out
    assert "0 %" in captured.out
    assert "90 %" in captured.out

def test_delete_chore(tmp_path, monkeypatch, capsys): 
    monkeypatch.chdir(tmp_path)
    filename = tmp_path / "Chores.csv"

    filename.write_text(
        "id,chore,credits,due,assignee,tick,frequency,original_day\n"
        "001,Dishes,3,2026-11-10,001: Patrick,Pending,None,None\n"
        "002,Laundry,5,2026-11-12,002: Jane,Pending,None,None\n"
    )
    inputs = iter(["1", "yes"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    delete_chore(filename)
    with open(filename, "r", newline="") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 1
    assert rows[0]["id"] == "002"
    captured = capsys.readouterr()
    assert "Chore deleted." in captured.out

    filename.write_text(
        "id,chore,credits,due,assignee,tick,frequency,original_day\n"
        "001,Dishes,3,2026-11-10,001: Patrick,Pending,None,None\n"
        "002,Laundry,5,2026-11-12,002: Jane,Pending,None,None\n"
    )
    inputs = iter(["001", "no"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    delete_chore(filename)
    with open(filename, "r", newline="") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 2
    captured = capsys.readouterr()
    assert "Deletion cancelled." in captured.out

    inputs = iter(["999"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    delete_chore(filename)
    with open(filename, "r", newline="") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 2
    captured = capsys.readouterr()
    assert "Chore not found." in captured.out  

def test_edit_delete_member(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    members_file = tmp_path / "Members.csv"
    chores_file = tmp_path / "Chores.csv"
    history_file = tmp_path / "CreditHistory.csv"

    members_file.write_text(
        "id,name,total_credits,monthly_target\n"
        "001,Patrick,10,20\n"
        "002,Jane,15,25\n"
    )
    chores_file.write_text(
        "id,chore,credits,due,assignee,tick,frequency,original_day\n"
        "001,Dishes,3,2026-11-10,001: Patrick,Pending,None,None\n"
        "002,Laundry,5,2026-11-12,002: Jane,Pending,None,None\n"
        "003,Mopping,4,2026-11-15,001: Patrick,Pending,None,None\n"
    )
    history_file.write_text(
        "member,chore,completion_date,credits\n"
    )

    inputs = iter(["delete", "001", "yes"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    edit_delete_member(members_file)
    with open(members_file, "r", newline="") as file:
        members = list(csv.DictReader(file))
    with open(chores_file, "r", newline="") as file:
        chores = list(csv.DictReader(file))
    assert len(members) == 1
    assert members[0]["id"] == "002"
    assert len(chores) == 3
    assert chores[0]["assignee"] == "None"
    assert chores[1]["assignee"] == "002: Jane"
    assert chores[2]["assignee"] == "None"

    inputs = iter(["delete", "002", "no"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    edit_delete_member(members_file)
    with open(members_file, "r", newline="") as file:
        members = list(csv.DictReader(file))
    with open(chores_file, "r", newline="") as file:
        chores = list(csv.DictReader(file))
    assert len(members) == 1
    assert len(chores) == 3
    assert chores[0]["assignee"] == "None"
    assert chores[1]["assignee"] == "002: Jane"
    assert chores[2]["assignee"] == "None"
    captured = capsys.readouterr()
    assert "Deletion cancelled." in captured.out

    inputs = iter(["delete", "999"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    edit_delete_member(members_file)
    with open(members_file, "r", newline="") as file:
        members = list(csv.DictReader(file))
    assert len(members) == 1
    captured = capsys.readouterr()
    assert "Member not found." in captured.out

    members_file.write_text(
        "id,name,total_credits,monthly_target\n"
        "001,Patrick,10,20\n"
        "002,Jane,15,25\n"
    )
    chores_file.write_text(
        "id,chore,credits,due,assignee,tick,frequency,original_day\n"
        "001,Dishes,3,2026-11-10,001: Patrick,Pending,None,None\n"
        "002,Laundry,5,2026-11-12,002: Jane,Pending,None,None\n"
        "003,Mopping,4,2026-11-15,001: Patrick,Pending,None,None\n"
    )
    history_file.write_text(
        "member,chore,completion_date,credits\n"
    )
   
    inputs = iter(["edit", "001", "Teresa"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    edit_delete_member(members_file)
    with open(members_file, "r", newline="") as file:
        members = list(csv.DictReader(file))
    assert members[0]["name"] == "Teresa"
    assert members[1]["name"] == "Jane"

    inputs = iter(["edit", "001", "", "cho"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    edit_delete_member(members_file)
    with open(members_file, "r", newline="") as file:
        members = list(csv.DictReader(file))
    assert members[0]["name"] == "Cho"
    captured = capsys.readouterr()
    assert "Member cannot be empty." in captured.out

    inputs = iter(["q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    edit_delete_member(members_file)
    with open(members_file, "r", newline="") as file:
        members = list(csv.DictReader(file))
    assert len(members) == 2
    captured = capsys.readouterr()
    assert "Deletion cancelled." in captured.out

def test_edit_chore(tmp_path, monkeypatch, capsys): 
    monkeypatch.chdir(tmp_path)
    chores_file = tmp_path / "Chores.csv"
    members_file = tmp_path / "Members.csv"
    def reset_files():
        chores_file.write_text(
            "id,chore,credits,due,assignee,tick,frequency,original_day\n"
            "001,Dishes,3,2026-11-10,001: Patrick,Pending,None,None\n"
            "002,Laundry,5,2026-11-12,002: Jane,Pending,Weekly,12\n"
            "003,Mopping,4,,None,Pending,None,\n"
        )
        members_file.write_text(
            "id,name,total_credits,monthly_target\n"
            "001,Patrick,10,20\n"
            "002,Jane,15,25\n"
        )

    reset_files()
    inputs = iter(["001", "chore", "washing dishes"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    edit_chore(chores_file)
    with open(chores_file,"r",newline="") as file: 
        reader = csv.DictReader(file)
        rows = list(reader)
    assert rows[0]["chore"] == "Washing Dishes"
    assert rows[1]["chore"] == "Laundry"
    captured = capsys.readouterr()
    assert "updated successfully" in captured.out

    reset_files()
    inputs = iter(["001", "credits", "abc", "15", "7"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    edit_chore(chores_file)
    with open(chores_file,"r",newline="") as file: 
        reader = csv.DictReader(file)
        rows = list(reader)
    assert rows[0]["credits"] == "7"
    captured = capsys.readouterr()
    assert "Invalid credits format." in captured.out
    assert "credits must be between 1-10." in captured.out

    reset_files()
    inputs = iter(["003", "frequency", "Weekly", "2026-11-20"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    edit_chore(chores_file)
    with open(chores_file,"r",newline="") as file: 
        reader = csv.DictReader(file)
        rows = list(reader)
    assert rows[2]["frequency"] == "Weekly"
    assert rows[2]["due"] == "2026-11-20"
    assert rows[2]["original_day"] == "20"

    reset_files()
    original_content = chores_file.read_text()
    inputs = iter(["002", "due", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    edit_chore(chores_file)
    assert chores_file.read_text() == original_content
    captured = capsys.readouterr()
    assert "Cannot delete due date for reccuring chores." in captured.out

def test_tick_chore(tmp_path, monkeypatch, capsys): 
    monkeypatch.chdir(tmp_path)
    chores_file = tmp_path / "Chores.csv"
    members_file = tmp_path / "Members.csv"
    history_file = tmp_path / "CreditHistory.csv"
    def reset_files():
        chores_file.write_text(
            "id,chore,credits,due,assignee,tick,frequency,original_day\n"
            "001,Dishes,3,2026-11-10,001: Patrick,Pending,None,\n"
            "002,Laundry,5,2026-11-12,002: Jane,Pending,Daily,12\n"
            "003,Mopping,4,2026-11-15,001: Patrick,Pending,Weekly,15\n"
            "004,Cooking,6,2026-11-30,002: Jane,Pending,Monthly,30\n"
            "005,Vacuuming,2,,None,Pending,None,\n"
            "006,Windows,3,2026-11-10,001: Patrick,Completed,None,\n"
        )
        members_file.write_text(
            "id,name,total_credits,monthly_target\n"
            "001,Patrick,10,20\n"
            "002,Jane,15,25\n"
        )
        history_file.write_text("")
    def read_csv(filename):
        with open(filename, "r", newline="") as file:
            return list(csv.DictReader(file))

    reset_files()
    inputs = iter(["001"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    tick_chore()
    chores = read_csv(chores_file)
    members = read_csv(members_file)
    history = read_csv(history_file)
    assert chores[0]["tick"] == "Completed"
    assert members[0]["total_credits"] == "13"
    assert len(history) == 1
    assert history[0]["member"] == "001: Patrick"
    assert history[0]["chore"] == "001: Dishes"
    assert history[0]["credits"] == "3"

    reset_files()
    inputs = iter(["005", "002"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    tick_chore()
    chores = read_csv(chores_file)
    members = read_csv(members_file)
    history = read_csv(history_file)
    assert chores[4]["tick"] == "Completed"
    assert chores[4]["assignee"] == "002: Jane"
    assert members[1]["total_credits"] == "17"
    assert history[0]["member"] == "002: Jane"
    assert history[0]["chore"] == "005: Vacuuming"

    reset_files()
    original_chores = chores_file.read_text()
    inputs = iter(["006"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    tick_chore()
    assert chores_file.read_text() == original_chores
    assert read_csv(history_file) == []
    captured = capsys.readouterr()
    assert "Chore already completed." in captured.out

    reset_files()
    inputs = iter(["004"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    tick_chore()
    chores = read_csv(chores_file)
    assert chores[-1]["id"] == "007"
    assert chores[-1]["due"] == "2026-12-30"
    assert chores[-1]["frequency"] == "Monthly"

def test_view_completion_history(tmp_path, monkeypatch, capsys): 
    monkeypatch.chdir(tmp_path)
    filename = tmp_path / "CreditHistory.csv"

    filename.write_text("member,chore,completion_date,credits\n")
    view_completion_history()
    captured = capsys.readouterr()
    assert "No history found." in captured.out

    filename.write_text(
        "member,chore,completion_date,credits\n"
        "001: Patrick,001: Dishes,2026-11-10,3\n"
        "002: Jane,002: Laundry,2026-11-11,5\n"
        "001: Patrick,003: Mopping,2026-11-12,4\n"
    )
    view_completion_history()
    captured = capsys.readouterr()
    assert "001: Patrick" in captured.out
    assert "002: Jane" in captured.out
    assert "001: Dishes" in captured.out
    assert "002: Laundry" in captured.out
    assert "003: Mopping" in captured.out
    assert "2026-11-10" in captured.out
    assert "2026-11-11" in captured.out
    assert "2026-11-12" in captured.out