import sqlite3
from datetime import datetime
import os
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
DB = "bot.db"

def init_db():
    conn = sqlite3.connect(DB)
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)",
        (
            user.id,
            user.first_name,
            user.username,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        )
    )

    cur.execute(
        "INSERT INTO messages (user_id, message, date) VALUES (?, ?, ?)",
        (
            user.id,
            text,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        )
    )

    conn.commit()
    conn.close()

    await update.message.reply_text("✅ تم استلام رسالتك")
    await context.bot.send_message(
        ADMIN_ID,
        f"📩 رسالة جديدة من {user.first_name}:\n\n{text}"
    )

def build_application() -> Application:
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app

