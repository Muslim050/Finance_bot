"""
Telethon userbot — listens to cardxabar bot and auto-forwards to your Finance Bot.

Run separately: python userbot.py
"""
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import User
import aiohttp

from config import (
    TELEGRAM_API_ID, TELEGRAM_API_HASH,
    CARDXABAR_BOT_USERNAME, BOT_TOKEN, ALLOWED_USER_ID
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Session file saved locally
client = TelegramClient('finance_userbot', TELEGRAM_API_ID, TELEGRAM_API_HASH)


async def send_to_bot(text: str):
    """Forward message text to our finance bot via Bot API."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with aiohttp.ClientSession() as session:
        await session.post(url, json={
            "chat_id": ALLOWED_USER_ID,
            "text": text
        })


@client.on(events.NewMessage(from_users=CARDXABAR_BOT_USERNAME))
async def handle_cardxabar_message(event):
    """Intercept every message from cardxabar and forward to finance bot."""
    text = event.raw_text
    if not text:
        return

    logger.info(f"Got cardxabar message: {text[:50]}...")

    if "Platezh" in text or "platezh" in text.lower():
        await send_to_bot(text)
        logger.info("Forwarded to finance bot")


async def main():
    await client.start()
    me = await client.get_me()
    logger.info(f"Userbot started as: {me.first_name} (@{me.username})")
    logger.info(f"Listening to: @{CARDXABAR_BOT_USERNAME}")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
