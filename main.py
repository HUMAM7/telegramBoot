import threading
import os

# تشغيل البوت
def run_bot():
    import bot
    bot.main()

# تشغيل لوحة التحكم
def run_dashboard():
    from dashboard import app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t1 = threading.Thread(target=run_bot)
    t1.start()

    run_dashboard()
