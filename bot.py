import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_USERNAME = "@hn_pz1"

WELCOME_TEXT = (
    "مرحبًا بك في بوت التواصل 🤍\n\n"
    "هذا البوت مخصص لاستقبال رسائلكم واستفساراتكم 📩\n"
    "يرجى إرسال رسالتك وسيتم إيصالها للإدارة 👨‍💼\n"
    "وسيتم الرد عليك في أقرب وقت ممكن ⏳\n\n"
    "للتواصل في حال وجود أي مشكلة ⚠️\n"
    "@hn_pz"
)

AFTER_SUB_TEXT = (
    WELCOME_TEXT + "\n\n"
    "✅ تم التحقق من اشتراكك بنجاح\n\n"
    "✍️ يمكنك الآن كتابة رسالتك مباشرة هنا\n"
    "📩 أي رسالة ترسلها ستصل للإدارة"
)

# ===== DATABASE =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    first_seen TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    date TEXT
)
""")
conn.commit()

async def is_subscribed(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if not await is_subscribed(context.bot, user.id):
        keyboard = [[
            InlineKeyboardButton("📢 اشترك في القناة", url="https://t.me/hn_pz1"),
            InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")
        ]]
        await update.message.reply_text(
            "🔒 يجب الاشتراك في القناة لاستخدام البوت:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    cursor.execute(
        "INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)",
        (user.id, user.first_name, user.username,
         datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()

    msg = await update.message.reply_text(AFTER_SUB_TEXT)
    await context.bot.pin_chat_message(user.id, msg.message_id)

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if await is_subscribed(context.bot, user.id):
        await query.message.delete()
        msg = await context.bot.send_message(user.id, AFTER_SUB_TEXT)
        await context.bot.pin_chat_message(user.id, msg.message_id)
    else:
        await query.message.reply_text("❌ لم يتم الاشتراك بعد")

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    if user.id == ADMIN_ID and context.user_data.get("reply_to"):
        target = context.user_data["reply_to"]
        await context.bot.send_message(target, f"📩 رد الإدارة:\n\n{text}")
        await update.message.reply_text("✅ تم إرسال الرد")
        context.user_data["reply_to"] = None
        return

    cursor.execute(
        "INSERT INTO messages (user_id, message, date) VALUES (?, ?, ?)",
        (user.id, text, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()

    await context.bot.send_message(ADMIN_ID, "🔔 لديك رسالة جديدة في بوت التواصل")

    keyboard = [[InlineKeyboardButton("✉️ الرد على المستخدم", callback_data=f"reply_{user.id}")]]
    await context.bot.send_message(
        ADMIN_ID,
        f"📩 رسالة جديدة\n\n👤 {user.first_name}\n🆔 {user.id}\n@{user.username}\n\n{text}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("✅ تم استلام رسالتك")

async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["reply_to"] = int(query.data.split("_")[1])
    await query.message.reply_text("✍️ اكتب ردك الآن:")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_subscription, pattern="check_sub"))
    app.add_handler(CallbackQueryHandler(reply_button, pattern="reply_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message))
    app.run_polling()

if __name__ == "__main__":
    main()
