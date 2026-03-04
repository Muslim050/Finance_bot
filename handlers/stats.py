from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.database import (
    get_monthly_stats, get_monthly_total,
    get_daily_spending, get_recent_transactions
)
from utils.charts import generate_pie_chart, generate_bar_chart
from config import ALLOWED_USER_ID

router = Router()


def month_keyboard(year: int, month: int):
    builder = InlineKeyboardBuilder()
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    builder.button(text="◀️", callback_data=f"stats:{prev_year}:{prev_month:02d}")
    builder.button(text="📊 По дням", callback_data=f"daily:{year}:{month:02d}")
    builder.button(text="▶️", callback_data=f"stats:{next_year}:{next_month:02d}")
    builder.adjust(3)
    return builder.as_markup()


async def send_stats(message_or_callback, year: int, month: int, edit=False):
    stats = await get_monthly_stats(year, month)
    total, count = await get_monthly_total(year, month)

    month_name = datetime(year, month, 1).strftime('%B %Y')

    if not stats:
        text = f"📭 Нет данных за {month_name}"
        if edit:
            await message_or_callback.message.edit_text(text)
        else:
            await message_or_callback.answer(text)
        return

    # Build text summary
    lines = [f"📊 <b>Расходы за {month_name}</b>\n"]
    lines.append(f"💰 Итого: <b>{total:,.0f} UZS</b>  |  {count} операций\n")

    for category, cat_total, cat_count in stats:
        pct = (cat_total / total * 100) if total else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        lines.append(
            f"{category}\n"
            f"  <code>{bar}</code> {pct:.1f}%\n"
            f"  {cat_total:,.0f} UZS  ({cat_count} op)\n"
        )

    text = "\n".join(lines)
    markup = month_keyboard(year, month)

    # Generate pie chart
    chart_buf = generate_pie_chart(stats, year, month, total)

    if chart_buf:
        chart_file = BufferedInputFile(chart_buf.read(), filename="stats.png")
        if edit:
            # Can't edit with photo easily, send new
            await message_or_callback.message.answer_photo(
                chart_file, caption=text, parse_mode="HTML", reply_markup=markup
            )
        else:
            await message_or_callback.answer_photo(
                chart_file, caption=text, parse_mode="HTML", reply_markup=markup
            )
    else:
        if edit:
            await message_or_callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
        else:
            await message_or_callback.answer(text, parse_mode="HTML", reply_markup=markup)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    now = datetime.now()
    await send_stats(message, now.year, now.month)


@router.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    await message.answer(
        "👋 <b>Finance Bot</b>\n\n"
        "Пересылай уведомления от @cardxabar_bot — я буду автоматически\n"
        "сохранять все траты и категоризировать их.\n\n"
        "<b>Команды:</b>\n"
        "/stats — статистика за текущий месяц\n"
        "/recent — последние 10 операций\n"
        "/categories — все известные магазины\n"
        "/help — помощь",
        parse_mode="HTML"
    )


@router.message(Command("recent"))
async def cmd_recent(message: Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    transactions = await get_recent_transactions(10)
    if not transactions:
        await message.answer("📭 Нет операций")
        return

    lines = ["🕐 <b>Последние операции:</b>\n"]
    for tx in transactions:
        tx_id, amount, currency, merchant, category, dt = tx
        cat = category or "❓"
        lines.append(f"{cat}  <b>{amount:,.0f} {currency}</b>  —  {merchant}\n<i>{dt}</i>\n")

    await message.answer("\n".join(lines), parse_mode="HTML")


@router.callback_query(F.data.startswith("stats:"))
async def handle_stats_nav(callback):
    _, year_str, month_str = callback.data.split(":")
    await send_stats(callback, int(year_str), int(month_str), edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("daily:"))
async def handle_daily_chart(callback):
    _, year_str, month_str = callback.data.split(":")
    year, month = int(year_str), int(month_str)

    daily_data = await get_daily_spending(year, month)
    if not daily_data:
        await callback.answer("Нет данных")
        return

    chart_buf = generate_bar_chart(daily_data, year, month)
    if chart_buf:
        month_name = datetime(year, month, 1).strftime('%B %Y')
        total = sum(row[1] for row in daily_data)
        avg = total / len(daily_data)

        chart_file = BufferedInputFile(chart_buf.read(), filename="daily.png")
        await callback.message.answer_photo(
            chart_file,
            caption=f"📈 <b>По дням — {month_name}</b>\n\n"
                    f"💰 Итого: <b>{total:,.0f} UZS</b>\n"
                    f"📊 Среднее в день: <b>{avg:,.0f} UZS</b>",
            parse_mode="HTML"
        )
    await callback.answer()
