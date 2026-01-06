from flask import Flask, render_template, request, redirect, session
import sqlite3
from users import DASHBOARD_USERS

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET"

def db():
    return sqlite3.connect("bot.db")

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

    conn = db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM messages")
    messages = c.fetchone()[0]

    c.execute("SELECT * FROM users ORDER BY first_seen DESC LIMIT 10")
    last_users = c.fetchall()

    c.execute("""
    SELECT messages.message, messages.date, users.name, users.username
    FROM messages JOIN users ON messages.user_id = users.user_id
    ORDER BY messages.date DESC LIMIT 10
    """)
    last_messages = c.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        users=users,
        messages=messages,
        last_users=last_users,
        last_messages=last_messages,
        username=session["user"]
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
