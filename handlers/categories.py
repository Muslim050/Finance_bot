from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from utils.database import get_all_merchant_categories
from config import ALLOWED_USER_ID

router = Router()


@router.message(Command("categories"))
async def cmd_categories(message: Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return

    mappings = await get_all_merchant_categories()
    if not mappings:
        await message.answer("📭 Нет сохранённых магазинов")
        return

    lines = ["🗂 <b>Известные магазины:</b>\n"]
    for merchant, category in mappings:
        lines.append(f"{category}  <code>{merchant}</code>")

    await message.answer("\n".join(lines), parse_mode="HTML")
