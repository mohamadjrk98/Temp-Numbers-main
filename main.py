
# main.py
import os
from telegram.ext import Application
from app.handlers import register_handlers
from app.config import Config
from app.logger import logger

def main():
    BOT_TOKEN = Config.BOT_TOKEN
    HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
    PORT = int(os.getenv('PORT', 10000))

    if not BOT_TOKEN or not HOSTNAME:
        logger.error("Missing BOT_TOKEN or RENDER_EXTERNAL_HOSTNAME.")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    register_handlers(app)

    WEBHOOK_URL = f"https://{HOSTNAME}/{BOT_TOKEN}"
    logger.info(f"🚀 Starting webhook at {WEBHOOK_URL}")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
