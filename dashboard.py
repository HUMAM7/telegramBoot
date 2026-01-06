from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from users import DASHBOARD_USERS

app = Flask(__name__, template_folder="templates")
app.secret_key = "super-secret-key-change-me"

DB = "bot.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u in DASHBOARD_USERS and DASHBOARD_USERS[u] == p:
            session["user"] = u
            return redirect("/")
        error = "بيانات غير صحيحة"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM messages")
    messages = cur.fetchone()[0]

    cur.execute("SELECT * FROM users ORDER BY first_seen DESC LIMIT 10")
    last_users = cur.fetchall()

    cur.execute("""
        SELECT messages.message, messages.date, users.name
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
