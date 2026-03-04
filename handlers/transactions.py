import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.parser import parse_cardxabar, normalize_merchant
from utils.database import (
    save_transaction, update_transaction_category,
    save_merchant_category, get_merchant_category
)
from utils.ai_categories import ai_categorize, get_categories
from config import ALLOWED_USER_ID

router = Router()


def build_category_keyboard(tx_id: int):
    builder = InlineKeyboardBuilder()
    for cat in get_categories():
        builder.button(text=cat, callback_data=f"cat:{tx_id}:{cat}")
    builder.adjust(2)
    return builder.as_markup()


@router.message(F.text.contains("Platezh") | F.text.contains("platezh"))
async def handle_cardxabar(message: Message):
    """Handle forwarded cardxabar messages."""
    if message.from_user.id != ALLOWED_USER_ID:
        return

    tx = parse_cardxabar(message.text)
    if not tx:
        return

    merchant_key = normalize_merchant(tx.merchant)

    # Step 1: Check if we already know this merchant
    known_category = await get_merchant_category(merchant_key)

    # Step 2: Save transaction (without category first)
    tx_id = await save_transaction(
        amount=tx.amount,
        currency=tx.currency,
        merchant=tx.merchant,
        card=tx.card,
        category=known_category,  # may be None
        datetime_str=tx.datetime_str,
        raw_message=tx.raw
    )

    balance_text = f"\n💵 Остаток: <b>{tx.balance:,.0f} {tx.currency}</b>" if tx.balance else ""

    if known_category:
        # We know this merchant — auto-categorize
        await message.reply(
            f"✅ <b>Транзакция сохранена</b>\n\n"
            f"💳 {tx.card}  |  📍 {tx.merchant}\n"
            f"➖ <b>{tx.amount:,.0f} {tx.currency}</b>\n"
            f"🏷 {known_category}{balance_text}\n\n"
            f"<i>Категория определена автоматически</i>",
            parse_mode="HTML"
        )
        return

    # Step 3: Try AI categorization
    await message.reply(
        f"💳 {tx.card}  |  📍 {tx.merchant}\n"
        f"➖ <b>{tx.amount:,.0f} {tx.currency}</b>{balance_text}\n\n"
        f"⏳ Определяю категорию...",
        parse_mode="HTML"
    )

    ai_category = await ai_categorize(tx.merchant, tx.amount, tx.currency)

    # Save AI suggestion but ask for confirmation
    reply_markup = build_category_keyboard(tx_id)
    await message.reply(
        f"💳 {tx.card}  |  📍 {tx.merchant}\n"
        f"➖ <b>{tx.amount:,.0f} {tx.currency}</b>{balance_text}\n\n"
        f"🤖 ИИ предлагает: <b>{ai_category}</b>\n\n"
        f"Подтверди или выбери другую категорию:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

    # Pre-set AI category (user can override)
    await update_transaction_category(tx_id, ai_category)


@router.callback_query(F.data.startswith("cat:"))
async def handle_category_selection(callback: CallbackQuery):
    """Handle category button press."""
    _, tx_id_str, category = callback.data.split(":", 2)
    tx_id = int(tx_id_str)

    await update_transaction_category(tx_id, category)

    # Remember this merchant → category mapping
    # We need to get merchant from original message
    msg_text = callback.message.reply_to_message.text if callback.message.reply_to_message else ""
    from utils.parser import parse_cardxabar, normalize_merchant
    tx = parse_cardxabar(msg_text)
    if tx:
        await save_merchant_category(normalize_merchant(tx.merchant), category)

    await callback.message.edit_text(
        callback.message.text.split("\n\n")[0] + f"\n\n✅ Категория: <b>{category}</b>",
        parse_mode="HTML"
    )
    await callback.answer("Сохранено!")
