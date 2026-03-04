import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "data/finance.db")


async def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'UZS',
                merchant TEXT,
                card TEXT,
                category TEXT,
                datetime TEXT,
                raw_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS merchant_categories (
                merchant TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                count INTEGER DEFAULT 1
            )
        """)
        await db.commit()


async def save_transaction(amount, currency, merchant, card, category, datetime_str, raw_message):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO transactions (amount, currency, merchant, card, category, datetime, raw_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (amount, currency, merchant, card, category, datetime_str, raw_message))
        await db.commit()
        return cursor.lastrowid


async def update_transaction_category(tx_id, category):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE transactions SET category = ? WHERE id = ?",
            (category, tx_id)
        )
        await db.commit()


async def save_merchant_category(merchant, category):
    """Remember merchant → category mapping for future auto-categorization."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO merchant_categories (merchant, category, count)
            VALUES (?, ?, 1)
            ON CONFLICT(merchant) DO UPDATE SET category = excluded.category, count = count + 1
        """, (merchant, category))
        await db.commit()


async def get_merchant_category(merchant):
    """Get known category for a merchant."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT category FROM merchant_categories WHERE merchant = ?", (merchant,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def get_monthly_stats(year, month):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM transactions
            WHERE strftime('%Y', datetime) = ? AND strftime('%m', datetime) = ?
              AND category IS NOT NULL
            GROUP BY category
            ORDER BY total DESC
        """, (str(year), f"{month:02d}")) as cursor:
            return await cursor.fetchall()


async def get_monthly_total(year, month):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT SUM(amount), COUNT(*)
            FROM transactions
            WHERE strftime('%Y', datetime) = ? AND strftime('%m', datetime) = ?
        """, (str(year), f"{month:02d}")) as cursor:
            row = await cursor.fetchone()
            return row[0] or 0, row[1] or 0


async def get_daily_spending(year, month):
    """Get daily totals for the month."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT strftime('%d', datetime) as day, SUM(amount)
            FROM transactions
            WHERE strftime('%Y', datetime) = ? AND strftime('%m', datetime) = ?
            GROUP BY day
            ORDER BY day
        """, (str(year), f"{month:02d}")) as cursor:
            return await cursor.fetchall()


async def get_recent_transactions(limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT id, amount, currency, merchant, category, datetime
            FROM transactions
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)) as cursor:
            return await cursor.fetchall()


async def get_all_merchant_categories():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT merchant, category FROM merchant_categories ORDER BY count DESC"
        ) as cursor:
            return await cursor.fetchall()
