"""
budget.py  --  the "brain" of the budget tracker.

This file holds ALL the logic and knows nothing about the web page.
Keeping logic separate from the interface is a habit worth building early:
you can test this file on its own, and you could later bolt a phone app
or a terminal menu onto it without changing a single line in here.

Concepts used: dictionaries, lists, functions, JSON files, f-strings.
"""

import json
import os
from datetime import date

# ---------------------------------------------------------------------------
# WHERE THE DATA LIVES
# ---------------------------------------------------------------------------
# __file__ is the path to this .py file. We build the path to data.json from
# it so the program works no matter which folder you run it from.
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# The categories a student actually spends on. Edit this list freely --
# the whole app reads from it, so adding one here makes it appear everywhere.
CATEGORIES = [
    "Food",
    "Rent",
    "Transport",
    "Airtime & Data",
    "Books & Stationery",
    "Entertainment",
    "Personal",
    "Savings",
]

# What an empty, brand-new budget looks like.
# "budget" = how much you plan to spend this month, "expenses" = the list.
DEFAULT_DATA = {"budget": 12000.0, "expenses": []}


# ---------------------------------------------------------------------------
# READING AND WRITING THE FILE
# ---------------------------------------------------------------------------
def load_data():
    """Read data.json and hand back a dictionary.

    If the file does not exist yet (first ever run), or somebody corrupts it,
    we quietly fall back to DEFAULT_DATA instead of crashing.
    """
    if not os.path.exists(DATA_FILE):
        return dict(DEFAULT_DATA)   # dict(...) makes a COPY, not a reference

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_DATA)

    # Defensive: make sure both keys exist even if the file is half-written.
    data.setdefault("budget", DEFAULT_DATA["budget"])
    data.setdefault("expenses", [])
    return data


def save_data(data):
    """Write the dictionary back to data.json.

    indent=2 makes the file human-readable -- open data.json in the workspace
    after adding an expense and you will see exactly what your code produced.
    """
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# CHANGING THE DATA
# ---------------------------------------------------------------------------
def next_id(expenses):
    """Work out the next unused id number.

    Every expense needs a unique id so we can delete the right one later.
    If the list is empty we start at 1; otherwise we take the biggest id
    currently in use and add one.
    """
    if not expenses:
        return 1
    return max(e["id"] for e in expenses) + 1


def add_expense(amount, category, note="", when=None):
    """Add one expense and save. Returns the expense that was created."""
    data = load_data()

    expense = {
        "id": next_id(data["expenses"]),
        "date": when or date.today().isoformat(),   # "2026-11-12"
        "category": category,
        "amount": round(float(amount), 2),
        "note": note.strip(),
    }

    data["expenses"].append(expense)
    save_data(data)
    return expense


def delete_expense(expense_id):
    """Remove the expense with this id.

    The list comprehension below means: "rebuild the list, keeping every
    expense whose id is NOT the one we want to delete."
    """
    data = load_data()
    data["expenses"] = [e for e in data["expenses"] if e["id"] != expense_id]
    save_data(data)


def set_budget(amount):
    """Change the monthly budget figure."""
    data = load_data()
    data["budget"] = round(float(amount), 2)
    save_data(data)


# ---------------------------------------------------------------------------
# ASKING QUESTIONS ABOUT THE DATA
# ---------------------------------------------------------------------------
def total_spent(expenses):
    """Add up every amount. sum() with a generator is the idiomatic way."""
    return sum(e["amount"] for e in expenses)


def totals_by_category(expenses):
    """Return {category: total} for categories that were actually used,
    sorted biggest first so the chart and the table read nicely."""
    totals = {}
    for e in expenses:
        # .get(key, 0) returns 0 when the category is not in the dict yet,
        # which saves writing an if-statement every time.
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]

    return dict(sorted(totals.items(), key=lambda pair: pair[1], reverse=True))


def summary():
    """Bundle up everything the page needs, so the web file stays tidy."""
    data = load_data()
    expenses = data["expenses"]
    this_month = date.today().isoformat()[:7]
    expenses = [e for e in expenses if e["date"].startswith(this_month)]
    budget = data["budget"]
    spent = total_spent(expenses)

    return {
        "budget": budget,
        "spent": spent,
        "remaining": budget - spent,
        # Guard against dividing by zero if the budget is set to 0.
        "percent_used": (spent / budget * 100) if budget > 0 else 0,
        "count": len(expenses),
        "this_month": this_month,
        "by_category": totals_by_category(expenses),
        # Newest first: sort by date, then by id to break ties.
        "expenses": sorted(expenses, key=lambda e: (e["date"], e["id"]), reverse=True),
    }


def money(value):
    """Format a number the way money should look: KSh 1,250.00"""
    return f"KSh {value:,.2f}"


# ---------------------------------------------------------------------------
# A QUICK SELF-TEST
# ---------------------------------------------------------------------------
# Everything below only runs when you type:  python3 budget.py
# It does NOT run when app.py imports this file. That is what the
# __name__ == "__main__" check is for -- a very common Python pattern.
if __name__ == "__main__":
    s = summary()
    print("Budget   :", money(s["budget"]))
    print("Spent    :", money(s["spent"]))
    print("Remaining:", money(s["remaining"]))
    print(f"Used     : {s['percent_used']:.1f}%")
    print(f"\n{s['count']} expense(s) recorded")
    for cat, amt in s["by_category"].items():
        print(f"  {cat:<20} {money(amt)}")
