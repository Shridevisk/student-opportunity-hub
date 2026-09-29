from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

DATABASE = "opportunities.db"


# ---------------- DATABASE ----------------

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def create_database():

    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            organization TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            eligibility TEXT NOT NULL,
            deadline TEXT NOT NULL,
            mode TEXT NOT NULL,
            location TEXT NOT NULL,
            application_link TEXT NOT NULL
        )
    """)

    count = db.execute(
        "SELECT COUNT(*) FROM opportunities"
    ).fetchone()[0]

    if count == 0:

        data = [

            (
                "AI/ML Internship",
                "Tech Innovations",
                "Internship",
                "Work on practical artificial intelligence and machine learning projects with an industry team.",
                "Engineering students with Python and basic machine learning knowledge.",
                "2026-10-05",
                "Hybrid",
                "Bengaluru",
                "https://example.com"
            ),

            (
                "Robotics Hackathon",
                "Robotics India",
                "Hackathon",
                "Build innovative robotics solutions for real-world engineering challenges.",
                "Engineering students and robotics enthusiasts.",
                "2026-10-10",
                "Offline",
                "Bengaluru",
                "https://example.com"
            ),

            (
                "National Coding Competition",
                "CodeArena",
                "Competition",
                "A coding competition focused on programming, algorithms and problem solving.",
                "College students and recent graduates.",
                "2026-10-18",
                "Online",
                "Online",
                "https://example.com"
            ),

            (
                "Data Science Workshop",
                "Analytics Community",
                "Workshop",
                "Hands-on workshop covering data analysis, visualization and machine learning fundamentals.",
                "Students interested in Data Science.",
                "2026-10-03",
                "Online",
                "Online",
                "https://example.com"
            ),

            (
                "Technology Scholarship",
                "FutureTech Foundation",
                "Scholarship",
                "Scholarship opportunity for students pursuing engineering and technology education.",
                "Eligible undergraduate students.",
                "2026-10-25",
                "Online",
                "India",
                "https://example.com"
            ),

            (
                "Software Development Internship",
                "Innovate Labs",
                "Internship",
                "Gain practical experience by contributing to real-world software development projects.",
                "Engineering students with programming fundamentals.",
                "2026-10-12",
                "Hybrid",
                "Bengaluru",
                "https://example.com"
            )

        ]

        db.executemany("""
            INSERT INTO opportunities
            (
                title,
                organization,
                category,
                description,
                eligibility,
                deadline,
                mode,
                location,
                application_link
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)

        db.commit()

    db.close()


# ---------------- DEADLINE STATUS ----------------

def add_deadline_status(opportunities):

    today = date.today()

    result = []

    for opportunity in opportunities:

        opportunity = dict(opportunity)

        deadline_date = datetime.strptime(
            opportunity["deadline"],
            "%Y-%m-%d"
        ).date()

        days_left = (deadline_date - today).days

        opportunity["days_left"] = days_left

        if days_left < 0:
            opportunity["deadline_status"] = "Closed"

        elif days_left <= 7:
            opportunity["deadline_status"] = "Urgent"

        elif days_left <= 14:
            opportunity["deadline_status"] = "Upcoming"

        else:
            opportunity["deadline_status"] = ""

        result.append(opportunity)

    return result


# ---------------- HOME ----------------

@app.route("/")
def home():

    db = get_db()

    opportunities = db.execute("""
        SELECT *
        FROM opportunities
        ORDER BY deadline ASC
        LIMIT 6
    """).fetchall()

    db.close()

    opportunities = add_deadline_status(opportunities)

    return render_template(
        "index.html",
        opportunities=opportunities
    )


# ---------------- OPPORTUNITIES ----------------

@app.route("/opportunities")
def opportunities():

    search = request.args.get(
        "search",
        ""
    ).strip()

    category = request.args.get(
        "category",
        "All"
    )

    db = get_db()

    query = """
        SELECT *
        FROM opportunities
        WHERE 1=1
    """

    values = []

    # Search
    if search:

        query += """
            AND (
                title LIKE ?
                OR organization LIKE ?
                OR description LIKE ?
            )
        """

        value = f"%{search}%"

        values.extend([
            value,
            value,
            value
        ])

    # Category
    if category != "All":

        query += """
            AND category = ?
        """

        values.append(category)

    query += """
        ORDER BY deadline ASC
    """

    opportunities_list = db.execute(
        query,
        values
    ).fetchall()

    db.close()

    opportunities_list = add_deadline_status(
        opportunities_list
    )

    categories = [
        "All",
        "Internship",
        "Hackathon",
        "Competition",
        "Scholarship",
        "Workshop"
    ]

    return render_template(
        "opportunities.html",
        opportunities=opportunities_list,
        categories=categories,
        selected_category=category,
        search=search
    )


# ---------------- DETAILS ----------------

@app.route("/opportunity/<int:id>")
def opportunity_details(id):

    db = get_db()

    opportunity = db.execute("""
        SELECT *
        FROM opportunities
        WHERE id = ?
    """, (id,)).fetchone()

    db.close()

    return render_template(
        "opportunity_details.html",
        opportunity=opportunity
    )


# ---------------- START ----------------

create_database()


if __name__ == "__main__":
    app.run(debug=True)