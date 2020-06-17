import datetime
import re
import shelve
import sys

CURRENT_DAY, CURRENT_MONTH, CURRENT_YEAR = datetime.datetime.today().strftime("%d.%m.%Y").split('.')
CURRENT_DAY, CURRENT_MONTH, CURRENT_YEAR = int(CURRENT_DAY), int(CURRENT_MONTH), int(CURRENT_YEAR)

TO_MONTHS = [1, 3, 5, 7, 8, 10, 12]
T_MONTHS = [4, 6, 9, 11]

SHELF_NAME = "goaltracker_data"
SHELF_PENDING_LIST = "GoalIndex"
SHELF_LAST_INDEX = -1
SHELF_LAST_INDEX_KEY = "LastIndex"
SHELF_FINISHED_LIST = "FinishedIndex"

MAIN_MENU_MESSAGE = "Press 'l' to list active goals, 'f' to list finished goals, 'a' to add a new goal, 'q' to quit."

with shelve.open(SHELF_NAME, writeback=True) as db:
    if SHELF_PENDING_LIST not in db:
        db[SHELF_PENDING_LIST] = []
    if SHELF_LAST_INDEX_KEY not in db:
        db[SHELF_LAST_INDEX_KEY] = SHELF_LAST_INDEX = -1
    else:
        SHELF_LAST_INDEX = db[SHELF_LAST_INDEX_KEY]
    if SHELF_FINISHED_LIST not in db:
        db[SHELF_FINISHED_LIST] = []

def check_finished() -> None:
    global CURRENT_DAY, CURRENT_MONTH, CURRENT_YEAR
    with shelve.open(SHELF_NAME, writeback=True) as db:
        for key in db[SHELF_PENDING_LIST]:
            row = db[key]
            b = datetime.datetime.strptime(f'{CURRENT_DAY}.{CURRENT_MONTH}.{CURRENT_YEAR}', "%d.%m.%Y")
            e = datetime.datetime.strptime(f'{row["DayEnding"]}.{row["MonthEnding"]}.{row["YearEnding"]}', "%d.%m.%Y")
            if (e-b).days <= 0:
                db[SHELF_PENDING_LIST].remove(key)
                db[SHELF_FINISHED_LIST].append(key)

def is_leap_year(year: int) -> bool:
    if year % 4 == 0:
        if year % 100 == 0 and year % 400 != 0:
            return False
        return True
    else:
        return False

def get_edate() -> dict:
    goal_edate = {}
    while True:
        date = input("Enter the goal's end date (in dd, dd.mm or dd.mm.YY format): ")
        try:
            day, month, year = date.split('.')
        except ValueError:
            try:
                day, month = date.split('.')
                year = CURRENT_YEAR
            except ValueError:
                day = date
                month, year = CURRENT_MONTH, CURRENT_YEAR
        try:
            day, month, year = int(day), int(month), int(year)
        except:
            print("{} does not match dd, dd.mm or dd.mm.YY format.".format(date))
            continue
        #if valid_date(day, month, year):
        goal_edate["Day"] = day
        goal_edate["Month"] = month
        goal_edate["Year"] = year
        return goal_edate
        print("{} is not a valid date.".format(date))

def add_entry() -> None:
    global SHELF_LAST_INDEX
    goal_bdate = {}
    goal_desc = input("Enter the goal's description: ")
    goal_bdate["Day"], goal_bdate["Month"], goal_bdate["Year"] = CURRENT_DAY, CURRENT_MONTH, CURRENT_YEAR
    goal_edate = get_edate()
    SHELF_LAST_INDEX += 1
    key = str(SHELF_LAST_INDEX)
    with shelve.open(SHELF_NAME, writeback=True) as db:
        db[SHELF_PENDING_LIST].append(key)
        db[key] = {}
        db[key]["Description"] = goal_desc
        db[key]["DayStarted"] = goal_bdate["Day"]
        db[key]["MonthStarted"] = goal_bdate["Month"]
        db[key]["YearStarted"] = goal_bdate["Year"]
        db[key]["DayEnding"] = goal_edate["Day"]
        db[key]["MonthEnding"] = goal_edate["Month"]
        db[key]["YearEnding"] = goal_edate["Year"]
        db[SHELF_LAST_INDEX_KEY] = SHELF_LAST_INDEX

def list_entries():
    with shelve.open(SHELF_NAME, writeback=True) as db:
        for key in db[SHELF_PENDING_LIST]:
            print("Started:\tEnding: \tLeft:\tDescription:")
            row = db[key]
            print(f'{row["DayStarted"]:02}.{row["MonthStarted"]:02}.{row["YearStarted"]}\t{row["DayEnding"]:02}.{row["MonthEnding"]:02}.{row["YearEnding"]}\t{get_time_left(db[key], db[key])}\t{row["Description"]}')

def list_finished():
    with shelve.open(SHELF_NAME, writeback=True) as db:
        for key in db[SHELF_FINISHED_LIST]:
            print("Started:\tEnded: \t\tDescription:")
            row = db[key]
            print(f'{row["DayStarted"]:02}.{row["MonthStarted"]:02}.{row["YearStarted"]}\t{row["DayEnding"]:02}.{row["MonthEnding"]:02}.{row["YearEnding"]}\t{row["Description"]}')

def get_time_left(bdate: dict, edate: dict) -> str:
    b = datetime.datetime.strptime(f'{bdate["DayStarted"]}.{bdate["MonthStarted"]}.{bdate["YearStarted"]}', "%d.%m.%Y")
    e = datetime.datetime.strptime(f'{edate["DayEnding"]}.{edate["MonthEnding"]}.{edate["YearEnding"]}', "%d.%m.%Y")
    days = (e-b).days
    if len(str(days)) >= 4: # If there are more than or equal 4 digits
        years = days // 365
        return str(years) + 'y'
    return str(days) + 'd'
        
def valid_date(day: int, month: int, year: int) -> bool:
    if ((year < CURRENT_YEAR) or
        (year == CURRENT_YEAR and month < CURRENT_MONTH) or
        (year == CURRENT_YEAR and month == CURRENT_MONTH and day < CURRENT_DAY)):
        return False
    if ((month in TO_MONTHS and day not in range(1, 32)) or
        (month in T_MONTHS and day not in range(1, 31))):
        return False
    if month == 2:
        if is_leap_year(year):
            if day not in range (1, 30):
                return False
        elif day not in range (1, 29):
            return False
    return True

def main():
    print(MAIN_MENU_MESSAGE)
    while True:
        check_finished()
        choice = input()
        if choice == 'l':
            list_entries()
        elif choice == 'a':
            add_entry()
        elif choice == 'f':
            list_finished()
        elif choice == 'q':
            sys.exit(0)
        else:
            print("Unknown option {}".format(choice))
            print(MAIN_MENU_MESSAGE)

if __name__ == "__main__":
    main()
