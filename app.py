from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from datetime import date, timedelta

app = Flask(__name__, static_folder="static", static_url_path="/static")
# =========================================================
# FLASK SETTINGS
# =========================================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "monagenda-local-development-key"
)

DB_PATH = "lifesync.db"

# =========================================================
# PET EMOJIS
# =========================================================
PET_EMOJIS = {
    "Panda": "🐼",
    "Cat": "🐱",
    "Dog": "🐶",
    "Bunny": "🐰",
    "Chick": "🐥",
    "Dinosaur": "🦖",
    "Duck": "🦆",
    "Penguin": "🐧",
    "Squirrel": "🐿️",
    "Dove": "🕊️",
    "Giraffe": "🦒",
    "Fish": "🐟",
    "Lion": "🦁",
    "Shark": "🦈",
    "Tiger": "🐯",
    "Elephant": "🐘",
    "Polar Bear": "🐻‍❄️",
    "Lizard": "🦎",
    "Butterfly": "🦋",
    "Owl": "🦉",
    "Horse": "🐴",
    "Goat": "🐐",
    "Monkey": "🐒",
    "Frog": "🐸",
    "Cow": "🐄",
    "Fox": "🦊",
    "Kangaroo": "🦘",
    "Hippo": "🦛",
    "Dolphin": "🐬",
    "Donkey": "🫏",
    "Camel": "🐪"
}
# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # =====================================================
    # USERS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            pet_name TEXT DEFAULT 'Boba',
            pet_type TEXT DEFAULT 'Panda',
            pet_level INTEGER DEFAULT 1,
            pet_happiness INTEGER DEFAULT 50,
            pet_treats INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )
    """)

    # =====================================================
    # HABITS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            streak INTEGER DEFAULT 0,
            last_completed_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # =====================================================
    # HABIT COMPLETION HISTORY
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habit_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            completed_date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # =====================================================
    # TIMETABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            subject TEXT NOT NULL,
            location TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # =====================================================
    # MEDICINES
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            reminder_time TEXT NOT NULL,
            last_taken_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # =====================================================
    # SKILLS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            user_id INTEGER PRIMARY KEY,
            can_teach TEXT DEFAULT '',
            want_learn TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # =====================================================
    # MOODS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mood TEXT NOT NULL,
            note TEXT,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# Initialize database when the application starts
init_db()


# =========================================================
# CURRENT USER
# =========================================================

def current_user():

    if "user_id" not in session:
        return None

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return user
# =========================================================
# MAKE PET EMOJI AVAILABLE TO ALL HTML PAGES
# =========================================================

@app.context_processor
def inject_pet_emojis():
    return {
        "pet_emojis": PET_EMOJIS
    }

# =========================================================
# XP SYSTEM
# =========================================================

def add_xp(amount=10):

    if "user_id" not in session:
        return

    conn = get_db()

    user = conn.execute(
        """
        SELECT xp, level
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    if not user:
        conn.close()
        return

    current_xp = user["xp"] or 0
    current_level = user["level"] or 1

    new_xp = current_xp + amount

    # Level increases every 100 XP
    new_level = (new_xp // 100) + 1

    # Prevent level from going backwards
    if new_level < current_level:
        new_level = current_level

    conn.execute(
        """
        UPDATE users
        SET xp = ?,
            level = ?
        WHERE id = ?
        """,
        (
            new_xp,
            new_level,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()


# =========================================================
# PET REWARD SYSTEM
# =========================================================

def add_treat(amount=2):

    if "user_id" not in session:
        return

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    if not user:
        conn.close()
        return

    current_treats = user["pet_treats"] or 0
    current_happiness = user["pet_happiness"] or 0
    current_pet_level = user["pet_level"] or 1

    new_treats = current_treats + amount

    new_happiness = min(
        100,
        current_happiness + 5
    )

    new_pet_level = current_pet_level

    # Pet levels up when happiness reaches 100
    if new_happiness >= 100:
        new_pet_level += 1
        new_happiness = 50

    conn.execute(
        """
        UPDATE users
        SET pet_treats = ?,
            pet_happiness = ?,
            pet_level = ?
        WHERE id = ?
        """,
        (
            new_treats,
            new_happiness,
            new_pet_level,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()
# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# =========================================================
# LOGIN / SIGN UP
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()

        if not username or not password:

            error = "Please fill in both fields."

        else:

            conn = get_db()

            user = conn.execute(
                """
                SELECT *
                FROM users
                WHERE username = ?
                AND password = ?
                """,
                (
                    username,
                    password
                )
            ).fetchone()

            # Existing user
            if user:

                session["user_id"] = user["id"]
                session["username"] = user["username"]

                conn.close()

                return redirect(
                    url_for("dashboard")
                )

            # New user
            else:

                try:

                    conn.execute(
                        """
                        INSERT INTO users
                        (username, password)
                        VALUES (?, ?)
                        """,
                        (
                            username,
                            password
                        )
                    )

                    conn.commit()

                    new_user = conn.execute(
                        """
                        SELECT *
                        FROM users
                        WHERE username = ?
                        """,
                        (username,)
                    ).fetchone()

                    session["user_id"] = new_user["id"]
                    session["username"] = new_user["username"]

                    conn.close()

                    return redirect(
                        url_for("dashboard")
                    )

                except sqlite3.IntegrityError:

                    error = (
                        "Username already exists. "
                        "Please use the correct password."
                    )

                    conn.close()

    return render_template(
        "login.html",
        error=error
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    happiness = user["pet_happiness"] or 0

    if happiness >= 80:

        pet_message = (
            f"😄 I'm feeling amazing today, {user['username']}! "
            "Let's complete all our goals together!"
        )

    elif happiness >= 50:

        pet_message = (
            "🙂 I'm doing okay. "
            "Complete some habits and let's grow together!"
        )

    else:

        pet_message = (
            "🥺 I need attention. "
            "Feed me or complete some tasks!"
        )

    # =====================================================
    # XP INFORMATION
    # =====================================================

    total_xp = user["xp"] or 0
    level = user["level"] or 1

    current_level_xp = total_xp % 100

    xp_progress = current_level_xp
    # =====================================================
    # HABIT STREAK INFORMATION
    # =====================================================

    conn = get_db()

    habit_rows = conn.execute(
        """
        SELECT streak, last_completed_date
        FROM habits
        WHERE user_id = ?
        """,
        (user["id"],)
    ).fetchall()

    conn.close()

    # Current streak = highest active streak
    current_streak = 0

    for habit in habit_rows:
        streak = habit["streak"] or 0

        if habit["last_completed_date"]:
            try:
                last_date = date.fromisoformat(
                    habit["last_completed_date"]
                )

                days_since = (
                    date.today() - last_date
                ).days

                # Only count streak if completed today or yesterday
                if days_since <= 1:
                    current_streak = max(
                        current_streak,
                        streak
                    )

            except ValueError:
                pass

    # Best streak
    best_streak = 0
    # =====================================================
    # WEEKLY HABIT COMPLETIONS
    # =====================================================

    today = date.today()

    # Monday = 0, Sunday = 6
    monday = today - timedelta(days=today.weekday())

    week_dates = [
        monday + timedelta(days=i)
        for i in range(7)
    ]

    conn = get_db()

    completion_rows = conn.execute(
        """
        SELECT DISTINCT completed_date
        FROM habit_completions
        WHERE user_id = ?
        """,
        (user["id"],)
    ).fetchall()

    conn.close()

    completed_dates = {
        row["completed_date"]
        for row in completion_rows
    }

    week_status = []

    for day_date in week_dates:
        week_status.append({
            "date": day_date,
            "completed": str(day_date) in completed_dates
        })

    for habit in habit_rows:
        best_streak = max(
            best_streak,
            habit["streak"] or 0
        )

    return render_template(
    "dashboard.html",
    user=user,
    pet_message=pet_message,
    xp=total_xp,
    level=level,
    xp_progress=xp_progress,
    current_streak=current_streak,
    best_streak=best_streak,
    week_status=week_status
)


# =========================================================
# HABITS
# =========================================================

@app.route("/habits")
def habits():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    conn = get_db()

    rows = conn.execute(
        """
        SELECT *
        FROM habits
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user["id"],)
    ).fetchall()

    conn.close()

    today = date.today()

    habit_list = []

    for h in rows:

        completed_today = (
            h["last_completed_date"] == str(today)
        )

        streak = h["streak"] or 0

        # Check if the habit has missed one or more days.
        # We don't immediately modify the database here;
        # the streak is corrected when the user completes it.
        if h["last_completed_date"]:

            try:

                last_date = date.fromisoformat(
                    h["last_completed_date"]
                )

                days_since = (
                    today - last_date
                ).days

                if days_since > 1:
                    streak = 0

            except ValueError:

                streak = 0

        habit_list.append({
            "id": h["id"],
            "name": h["name"],
            "streak": streak,
            "completed_today": completed_today
        })

    return render_template(
    "habits.html",
    habits=habit_list,
    user=user
)


# =========================================================
# ADD HABIT
# =========================================================

@app.route("/habits/add", methods=["POST"])
def add_habit():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    name = request.form.get(
        "habit_name",
        ""
    ).strip()

    if name:

        conn = get_db()

        conn.execute(
            """
            INSERT INTO habits
            (user_id, name, streak, last_completed_date)
            VALUES (?, ?, 0, NULL)
            """,
            (
                user["id"],
                name
            )
        )

        conn.commit()
        conn.close()

    return redirect(
        url_for("habits")
    )


# =========================================================
# DELETE HABIT
# =========================================================

@app.route(
    "/habits/delete/<int:habit_id>",
    methods=["POST"]
)
def delete_habit(habit_id):

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    conn = get_db()

    conn.execute(
        """
        DELETE FROM habits
        WHERE id = ?
        AND user_id = ?
        """,
        (
            habit_id,
            user["id"]
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("habits")
    )


# =========================================================
# COMPLETE HABIT
# =========================================================

@app.route(
    "/habits/complete/<int:habit_id>",
    methods=["POST"]
)
def complete_habit(habit_id):

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    today = date.today()
    today_string = str(today)

    conn = get_db()

    habit = conn.execute(
        """
        SELECT *
        FROM habits
        WHERE id = ?
        AND user_id = ?
        """,
        (
            habit_id,
            user["id"]
        )
    ).fetchone()

    if not habit:

        conn.close()

        return redirect(
            url_for("habits")
        )

    # =====================================================
    # PREVENT DOUBLE COMPLETION
    # =====================================================

    if habit["last_completed_date"] == today_string:

        conn.close()

        return redirect(
            url_for("habits")
        )

    # =====================================================
    # CALCULATE STREAK
    # =====================================================

    old_streak = habit["streak"] or 0

    if habit["last_completed_date"]:

        try:

            last_date = date.fromisoformat(
                habit["last_completed_date"]
            )

            days_since = (
                today - last_date
            ).days

            # Completed yesterday → continue streak
            if days_since == 1:

                new_streak = old_streak + 1

            # Missed one or more days → restart
            else:

                new_streak = 1

        except ValueError:

            new_streak = 1

    else:

        # First completion
        new_streak = 1

    # =====================================================
    # UPDATE HABIT
    # =====================================================

    conn.execute(
        """
        UPDATE habits
        SET streak = ?,
            last_completed_date = ?
        WHERE id = ?
        AND user_id = ?
        """,
        (
            new_streak,
            today_string,
            habit_id,
            user["id"]
        )
    )

    # =====================================================
    # SAVE COMPLETION HISTORY
    # =====================================================

    conn.execute(
        """
        INSERT INTO habit_completions
        (habit_id, user_id, completed_date)
        VALUES (?, ?, ?)
        """,
        (
            habit_id,
            user["id"],
            today_string
        )
    )

    conn.commit()
    conn.close()
    # =====================================================
    # REWARDS
    # =====================================================

    # +10 XP
    add_xp(10)

    # +2 Treats
    add_treat(2)

    return redirect(
        url_for("habits")
    )
# =========================================================
# TIMETABLE
# =========================================================

@app.route("/timetable")
def timetable():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    conn = get_db()

    rows = conn.execute(
        """
        SELECT *
        FROM classes
        WHERE user_id = ?
        ORDER BY time
        """,
        (user["id"],)
    ).fetchall()

    conn.close()

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday"
    ]

    timetable_data = {}

    for day in day_order:
        timetable_data[day] = []

    for row in rows:

        if row["day"] in timetable_data:

            timetable_data[row["day"]].append({
                "id": row["id"],
                "time": row["time"],
                "subject": row["subject"],
                "location": row["location"]
            })

    return render_template(
    "timetable.html",
    timetable=timetable_data,
    day_order=day_order,
    user=user
)


# =========================================================
# ADD CLASS
# =========================================================

@app.route("/timetable/add", methods=["POST"])
def add_class():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    day = request.form.get(
        "day",
        ""
    ).strip()

    time = request.form.get(
        "time",
        ""
    ).strip()

    subject = request.form.get(
        "subject",
        ""
    ).strip()

    location = request.form.get(
        "location",
        ""
    ).strip()

    if day and time and subject:

        conn = get_db()

        conn.execute(
            """
            INSERT INTO classes
            (user_id, day, time, subject, location)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                day,
                time,
                subject,
                location
            )
        )

        conn.commit()
        conn.close()

    return redirect(
        url_for("timetable")
    )


# =========================================================
# DELETE CLASS
# =========================================================

@app.route(
    "/timetable/delete/<int:class_id>"
)
def delete_class(class_id):

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    conn = get_db()

    conn.execute(
        """
        DELETE FROM classes
        WHERE id = ?
        AND user_id = ?
        """,
        (
            class_id,
            user["id"]
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("timetable")
    )


# =========================================================
# MEDICINES
# =========================================================
@app.route("/medicine")
def medicine():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    conn = get_db()

    rows = conn.execute(
        """
        SELECT *
        FROM medicines
        WHERE user_id = ?
        ORDER BY reminder_time
        """,
        (user["id"],)
    ).fetchall()

    medicines = []

    for row in rows:

        medicines.append({
            "id": row["id"],
            "name": row["name"],
            "dosage": row["dosage"],
            "reminder_time": row["reminder_time"],
            "taken_today": (
                row["last_taken_date"] == str(date.today())
            )
        })

    conn.close()

    return render_template(
        "medicine.html",
        user=user,
        medicines=medicines
    )

# =========================================================
# ADD MEDICINE
# =========================================================

@app.route(
    "/medicine/add",
    methods=["POST"]
)
def add_medicine():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    name = request.form.get(
        "med_name",
        ""
    ).strip()

    dosage = request.form.get(
        "dosage",
        ""
    ).strip()

    reminder_time = request.form.get(
        "reminder_time",
        ""
    ).strip()

    if name and dosage and reminder_time:

        conn = get_db()

        conn.execute(
            """
            INSERT INTO medicines
            (user_id, name, dosage, reminder_time)
            VALUES (?, ?, ?, ?)
            """,
            (
                user["id"],
                name,
                dosage,
                reminder_time
            )
        )

        conn.commit()
        conn.close()

    return redirect(
        url_for("medicine")
    )


# =========================================================
# TAKE MEDICINE
# =========================================================

@app.route(
    "/medicine/take/<int:med_id>"
)
def take_medicine(med_id):

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    today = str(date.today())

    conn = get_db()

    medicine = conn.execute(
        """
        SELECT *
        FROM medicines
        WHERE id = ?
        AND user_id = ?
        """,
        (
            med_id,
            user["id"]
        )
    ).fetchone()

    if medicine:

        if medicine["last_taken_date"] == today:

            conn.close()

            return redirect(
                url_for("medicine")
            )

        conn.execute(
            """
            UPDATE medicines
            SET last_taken_date = ?
            WHERE id = ?
            AND user_id = ?
            """,
            (
                today,
                med_id,
                user["id"]
            )
        )

        conn.commit()
        conn.close()

        # +5 XP
        add_xp(5)

        # +1 Treat
        add_treat(1)

    else:

        conn.close()

    return redirect(
        url_for("medicine")
    )


# =========================================================
# SKILLSWAP
# =========================================================

@app.route("/skills")
def skills():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    conn = get_db()

    profile = conn.execute(
        """
        SELECT *
        FROM skills
        WHERE user_id = ?
        """,
        (user["id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "skill_swap.html",
        profile=profile,
        user=user
    )


# =========================================================
# UPDATE SKILLS
# =========================================================

@app.route(
    "/skills/update",
    methods=["POST"]
)
def update_skills():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    can_teach = request.form.get(
        "can_teach",
        ""
    ).strip()

    want_learn = request.form.get(
        "want_learn",
        ""
    ).strip()

    conn = get_db()

    existing = conn.execute(
        """
        SELECT *
        FROM skills
        WHERE user_id = ?
        """,
        (user["id"],)
    ).fetchone()

    if existing:

        conn.execute(
            """
            UPDATE skills
            SET can_teach = ?,
                want_learn = ?
            WHERE user_id = ?
            """,
            (
                can_teach,
                want_learn,
                user["id"]
            )
        )

    else:

        conn.execute(
            """
            INSERT INTO skills
            (user_id, can_teach, want_learn)
            VALUES (?, ?, ?)
            """,
            (
                user["id"],
                can_teach,
                want_learn
            )
        )

    conn.commit()
    conn.close()

    return redirect(
        url_for("skills")
    )





# =========================================================
# PET COACH
# =========================================================

@app.route("/pets")
def pets():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    return render_template(
        "pets.html",
        user=user
    )


# =========================================================
# FEED PET
# =========================================================

@app.route(
    "/feed_pet",
    methods=["POST"]
)
def feed_pet():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    conn = get_db()

    fresh_user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user["id"],)
    ).fetchone()

    if fresh_user:

        current_treats = fresh_user["pet_treats"] or 0
        current_happiness = fresh_user["pet_happiness"] or 0

        # Feeding costs 5 treats
        if current_treats >= 5:

            new_treats = current_treats - 5

            new_happiness = min(
                100,
                current_happiness + 10
            )

            conn.execute(
                """
                UPDATE users
                SET pet_treats = ?,
                    pet_happiness = ?
                WHERE id = ?
                """,
                (
                    new_treats,
                    new_happiness,
                    fresh_user["id"]
                )
            )

            conn.commit()

    conn.close()

    return redirect(
        url_for("pets")
    )


# =========================================================
# UPDATE PET
# =========================================================

@app.route(
    "/update_pet",
    methods=["POST"]
)
def update_pet():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    pet_name = request.form.get(
        "pet_name",
        "Boba"
    ).strip()

    pet_type = request.form.get(
        "pet_type",
        "Panda"
    ).strip()

    if not pet_name:
        pet_name = "Boba"

    allowed_pets = [
        "Panda",
        "Cat",
        "Dog",
        "Bunny",
        "Chick",
        "Dinosaur",
        "Duck",
        "Penguin",
        "Squirrel",
        "Dove",
        "Giraffe",
        "Fish",
        "Lion",
        "Shark",
        "Tiger",
        "Elephant",
        "Polar Bear",
        "Lizard",
        "Butterfly",
        "Owl",
        "Horse",
        "Goat",
        "Monkey",
        "Frog",
        "Cow",
        "Fox",
        "Kangaroo",
        "Hippo",
        "Dolphin",
        "Donkey",
        "Camel"
    ]

    if pet_type not in allowed_pets:
        pet_type = "Panda"

    conn = get_db()

    conn.execute(
        """
        UPDATE users
        SET pet_name = ?,
            pet_type = ?
        WHERE id = ?
        """,
        (
            pet_name,
            pet_type,
            user["id"]
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("pets")
    )
# =========================================================
# MOOD TRACKER
# =========================================================

@app.route("/mood", methods=["GET", "POST"])
def mood():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    conn = get_db()

    if request.method == "POST":

        selected_mood = request.form.get("mood")

        if selected_mood:

            conn.execute(
                """
                INSERT INTO moods
                (user_id, mood, date)
                VALUES (?, ?, ?)
                """,
                (
                    user["id"],
                    selected_mood,
                    str(date.today())
                )
            )

            conn.commit()

    latest_mood = conn.execute(
        """
        SELECT *
        FROM moods
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user["id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "mood.html",
        user=user,
        latest_mood=latest_mood
    )
@app.route("/mental_health")
def mental_health():
    return render_template("mental_health.html")
# =========================================================
# PETBOT
# =========================================================

@app.route("/petbot")
def petbot():

    user = current_user()

    if not user:
        return redirect(url_for("login"))

    return render_template(
        "petbot.html",
        user=user
    )
    # =========================================================
# PETBOT CHAT API
# =========================================================

@app.route("/petbot/chat", methods=["POST"])
def petbot_chat():

    user = current_user()

    if not user:
        return {
            "success": False,
            "response": "Please login first."
        }, 401

    data = request.get_json()

    if not data:
        return {
            "success": False,
            "response": "I didn't receive your message."
        }, 400

    message = data.get("message", "").strip()

    if not message:
        return {
            "success": False,
            "response": "Tell me something! 🐾"
        }, 400

    # =====================================================
    # PET INFORMATION
    # =====================================================

    pet_name = user["pet_name"] or "Boba"
    pet_type = user["pet_type"] or "Panda"
    happiness = user["pet_happiness"] or 50
    pet_level = user["pet_level"] or 1

    message_lower = message.lower()

    # =====================================================
    # PETBOT BRAIN
    # =====================================================

    if any(word in message_lower for word in [
        "sad",
        "upset",
        "cry",
        "bad",
        "depressed"
    ]):

        response = (
            f"Hey, I'm here with you. 🐾💜 "
            f"You don't have to handle everything alone. "
            f"Take a small breath and tell me what's bothering you."
        )

    elif any(word in message_lower for word in [
        "motivate",
        "motivation",
        "lazy",
        "can't do",
        "give up"
    ]):

        response = (
            f"Come on! 🐾 {pet_name} believes in you! "
            f"You don't need to finish everything right now. "
            f"Just start with one tiny task for 10 minutes. "
            f"Once you start, I'll stay with you!"
        )

    elif any(word in message_lower for word in [
        "study",
        "exam",
        "assignment",
        "college",
        "learn"
    ]):

        response = (
            f"📚 Study mode activated! "
            f"Let's make it simple: choose one topic, "
            f"focus for 25 minutes, then take a 5-minute break. "
            f"I'll be your study buddy, okay? 🐾"
        )

    elif any(word in message_lower for word in [
        "focus",
        "concentrate",
        "distracted"
    ]):

        response = (
            f"🎯 Let's focus together! "
            f"Put your phone away, choose ONE task, "
            f"and work on it for just 10 minutes. "
            f"Your {pet_type} buddy is watching! 🐾"
        )

    elif any(word in message_lower for word in [
        "hello",
        "hi",
        "hey"
    ]):

        response = (
            f"Hey! 👋 I'm {pet_name}, your {pet_type} companion! "
            f"I'm currently at pet level {pet_level} "
            f"with {happiness}% happiness. 🐾 "
            f"What are we doing today?"
        )

    elif any(word in message_lower for word in [
        "happy",
        "good",
        "great",
        "awesome"
    ]):

        response = (
            f"Yayyy! 🐾💜 I love hearing that! "
            f"Let's use that energy to accomplish something awesome today!"
        )

    elif any(word in message_lower for word in [
        "tired",
        "sleepy",
        "exhausted"
    ]):

        response = (
            f"Sounds like you need a little break. 🐾 "
            f"Drink some water, relax for a few minutes, "
            f"and then decide whether you need rest or a small task."
        )

    else:

        response = (
            f"Hmm... 🐾 I'm listening! "
            f"Tell me a little more about that. "
            f"I want to understand what you're thinking."
        )

    return {
        "success": True,
        "response": response,
        "pet_name": pet_name,
        "pet_type": pet_type
    }

# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )