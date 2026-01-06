import threading
import os

def run_bot():
    import bot
    bot.main()

def run_dashboard():
    from dashboard import app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.daemon = True          # ⭐⭐⭐ هذا السطر هو الحل
    t.start()

    run_dashboard()
