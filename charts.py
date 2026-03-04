import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
from datetime import datetime


COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#82E0AA', '#F0B27A', '#AED6F1', '#A9DFBF', '#FAD7A0'
]


def format_amount(amount: float) -> str:
    """Format amount with thousand separators."""
    if amount >= 1_000_000:
        return f"{amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"{amount/1_000:.0f}K"
    return f"{amount:.0f}"


def generate_pie_chart(stats: list, year: int, month: int, total: float) -> io.BytesIO:
    """Generate pie chart for category breakdown."""
    if not stats:
        return None

    categories = [row[0] for row in stats]
    amounts = [row[1] for row in stats]

    # Merge small categories into "Other"
    threshold = total * 0.03
    main_cats = [(c, a) for c, a in zip(categories, amounts) if a >= threshold]
    small_sum = sum(a for c, a in zip(categories, amounts) if a < threshold)
    if small_sum > 0:
        main_cats.append(("🔸 Прочее", small_sum))

    labels = [c for c, _ in main_cats]
    values = [a for _, a in main_cats]

    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        colors=COLORS[:len(values)],
        autopct=lambda p: f'{p:.1f}%' if p > 4 else '',
        startangle=90,
        pctdistance=0.75,
        wedgeprops=dict(width=0.6, edgecolor='#1a1a2e', linewidth=2)
    )

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')

    month_name = datetime(year, month, 1).strftime('%B %Y')
    ax.set_title(
        f'Расходы за {month_name}\n{format_amount(total)} UZS',
        color='white', fontsize=14, fontweight='bold', pad=20
    )

    # Legend
    legend_labels = [f'{cat}  {format_amount(val)} UZS' for cat, val in zip(labels, values)]
    patches = [mpatches.Patch(color=COLORS[i], label=legend_labels[i]) for i in range(len(labels))]
    legend = ax.legend(
        handles=patches, loc='lower center',
        bbox_to_anchor=(0.5, -0.15),
        ncol=2, fontsize=9,
        facecolor='#16213e', edgecolor='#0f3460',
        labelcolor='white'
    )

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    buf.seek(0)
    plt.close()
    return buf


def generate_bar_chart(daily_data: list, year: int, month: int) -> io.BytesIO:
    """Generate bar chart of daily spending."""
    if not daily_data:
        return None

    days = [int(row[0]) for row in daily_data]
    amounts = [row[1] for row in daily_data]

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')

    bars = ax.bar(days, amounts, color='#4ECDC4', alpha=0.8, edgecolor='#1a1a2e', linewidth=0.5)

    # Highlight max day
    max_idx = amounts.index(max(amounts))
    bars[max_idx].set_color('#FF6B6B')

    ax.set_xlabel('День месяца', color='#aaaaaa', fontsize=10)
    ax.set_ylabel('Сумма (UZS)', color='#aaaaaa', fontsize=10)

    month_name = datetime(year, month, 1).strftime('%B %Y')
    ax.set_title(f'Траты по дням — {month_name}', color='white', fontsize=13, fontweight='bold')

    ax.tick_params(colors='#aaaaaa')
    ax.spines['bottom'].set_color('#333355')
    ax.spines['left'].set_color('#333355')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Value labels on bars
    for bar, amount in zip(bars, amounts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(amounts) * 0.01,
            format_amount(amount),
            ha='center', va='bottom', color='white', fontsize=7, fontweight='bold'
        )

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: format_amount(x)))
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    buf.seek(0)
    plt.close()
    return buf
