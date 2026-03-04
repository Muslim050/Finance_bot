import anthropic
import json
from config import ANTHROPIC_API_KEY

CATEGORIES = [
    "🍕 Еда и рестораны",
    "🛒 Продукты",
    "🚗 Транспорт",
    "🏠 Жильё и ЖКХ",
    "💊 Здоровье",
    "👗 Одежда",
    "🎮 Развлечения",
    "📱 Связь и интернет",
    "🏦 Банк и кредиты",
    "🛍️ Покупки",
    "✈️ Путешествия",
    "💼 Работа и бизнес",
    "🎓 Образование",
    "❓ Другое",
]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


async def ai_categorize(merchant: str, amount: float, currency: str) -> str:
    """Use Claude to guess category based on merchant name."""
    try:
        categories_list = "\n".join(f"- {c}" for c in CATEGORIES)
        prompt = f"""Определи категорию расхода по названию магазина/сервиса.

Магазин: {merchant}
Сумма: {amount:,.0f} {currency}

Доступные категории:
{categories_list}

Ответь ТОЛЬКО JSON в формате: {{"category": "название категории"}}
Выбери наиболее подходящую категорию из списка."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()
        # Clean possible markdown
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(response_text)
        category = data.get("category", "❓ Другое")

        # Validate it's one of our categories
        if category in CATEGORIES:
            return category
        # Try partial match
        for cat in CATEGORIES:
            if cat.split(" ", 1)[1].lower() in category.lower():
                return cat
        return "❓ Другое"

    except Exception:
        return "❓ Другое"


def get_categories() -> list[str]:
    return CATEGORIES
