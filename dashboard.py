from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from users import DASHBOARD_USERS

app = Flask(__name__)
app.secret_key = "super-secret-key-change-me"

# ================= DATABASE =================
DB_PATH = os.path.join(os.getcwd(), "bot.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        username TEXT,
        first_seen TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

init_db()

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in DASHBOARD_USERS and DASHBOARD_USERS[username] == password:
            session["user"] = username
            return redirect("/")
        else:
            error = "بيانات الدخول غير صحيحة"

    return render_template("login.html", error=error)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= DASHBOARD =================
@app.route("/")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM users")
        users = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM messages")
        messages = cur.fetchone()[0]

        cur.execute("SELECT * FROM users ORDER BY first_seen DESC LIMIT 10")
        last_users = cur.fetchall()

        cur.execute("""
            SELECT messages.message, messages.date, users.name, users.username
            FROM messages
            LEFT JOIN users ON messages.user_id = users.user_id
            ORDER BY messages.date DESC
            LIMIT 10
        """)
        last_messages = cur.fetchall()

        conn.close()

        return render_template(
            "dashboard.html",
            users=users,
            messages=messages,
            last_users=last_users,
            last_messages=last_messages,
            username=session["user"]
        )

    except Exception as e:
        return f"<h3>Internal Error</h3><pre>{e}</pre>"

# ================= RUN =================
