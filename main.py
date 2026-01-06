import os
from dashboard import app, tg_app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    tg_app.initialize()
    tg_app.start()

    app.run(
        host="0.0.0.0",
        port=port,
        use_reloader=False
    )
