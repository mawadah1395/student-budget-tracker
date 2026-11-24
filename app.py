"""
app.py  --  the web page.

Flask's job is small: listen for a request from the browser, call the right
function in budget.py, and hand the result to the HTML template.

A "route" is just a URL plus the function that answers it.
"""

from flask import Flask, render_template, request, redirect, url_for

import budget
from chart import pie_chart_svg, legend_colour

app = Flask(__name__)


# ---------------------------------------------------------------------------
# THE DASHBOARD  --  what you see at the home page "/"
# ---------------------------------------------------------------------------
@app.route("/")
def dashboard():
    data = budget.summary()

    # Build the pie chart and attach a matching colour to each category so the
    # legend and the chart agree.
    chart_svg = pie_chart_svg(data["by_category"])
    legend = [
        {
            "category": category,
            "amount": amount,
            "colour": legend_colour(i),
            "share": amount / data["spent"] * 100 if data["spent"] > 0 else 0,
        }
        for i, (category, amount) in enumerate(data["by_category"].items())
    ]

    return render_template(
        "index.html",
        data=data,
        chart_svg=chart_svg,
        legend=legend,
        categories=budget.CATEGORIES,
        money=budget.money,          # pass the helper so the template can use it
        today=budget.date.today().isoformat(),
    )


# ---------------------------------------------------------------------------
# ACTIONS  --  these change data, then send you back to the dashboard
# ---------------------------------------------------------------------------
# methods=["POST"] means this route only answers form submissions,
# not someone typing the URL into their browser.
@app.route("/add", methods=["POST"])
def add():
    amount = request.form.get("amount", "").strip()
    category = request.form.get("category", "Food")
    note = request.form.get("note", "")
    when = request.form.get("date") or None

    # Never trust what comes from a form. If the amount is blank or not a
    # number, float() raises ValueError -- so we catch it and ignore the entry
    # rather than showing the user a crash page.
    try:
        value = float(amount)
        if value > 0:
            budget.add_expense(value, category, note, when)
    except ValueError:
        pass

    # redirect() after a POST stops the browser re-submitting the form when
    # someone hits refresh. This is a standard web pattern worth knowing.
    return redirect(url_for("dashboard"))


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    # <int:expense_id> in the URL means Flask grabs the number out of the
    # address (/delete/7) and passes it in as an argument. Nice and tidy.
    budget.delete_expense(expense_id)
    return redirect(url_for("dashboard"))


@app.route("/budget", methods=["POST"])
def change_budget():
    try:
        budget.set_budget(float(request.form.get("budget", 0)))
    except ValueError:
        pass
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    # host="0.0.0.0" makes the server reachable from outside this sandbox,
    # which is what lets the live preview appear in your browser.
    app.run(host="0.0.0.0", port=5000, debug=False)
