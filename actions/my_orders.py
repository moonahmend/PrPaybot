from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3

async def my_orders(update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    telegram_id = user.id
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, order_type TEXT, details TEXT, amount INTEGER, created_at TEXT)")
    c.execute("SELECT order_type, details, amount, created_at FROM orders WHERE telegram_id = ? ORDER BY created_at DESC", (telegram_id,))
    orders = c.fetchall()
    print("DEBUG: Orders fetched for telegram_id =", telegram_id, "orders =", orders)
    if not orders:
        message = (
            "📦 <b>My Orders</b>\n\n"
            "You have not placed any orders yet."
        )
    else:
        message = "📦 <b>My Orders</b>\n\n"
        for order in orders:
            message += f"• <b>{order[0].capitalize()}</b>: {order[1]} ({order[2]} tokens)\n  <i>{order[3][:19].replace('T', ' ')}</i>\n\n"
        if message.strip() == "📦 <b>My Orders</b>":
            message += "\n(You have orders, but they could not be displayed due to a formatting issue.)"
    keyboard = [
        [InlineKeyboardButton("← Back to Menu", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='HTML')
    conn.close()