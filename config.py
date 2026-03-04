import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))  # your Telegram user ID

# Telethon userbot
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
CARDXABAR_BOT_USERNAME = os.getenv("CARDXABAR_BOT_USERNAME", "cardxabar_bot")
