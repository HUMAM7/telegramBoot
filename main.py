import os
import asyncio
from dashboard import app, tg_app
async def start_all():
    await tg_app.initialize()
    await tg_app.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    # تشغيل Telegram Application بشكل صحيح
    asyncio.run(start_all())

    # تشغيل Flask
    app.run(
        host="0.0.0.0",
        port=port,
        use_reloader=False
    )
