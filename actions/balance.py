from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3

async def balance(update, context):
    print('DEBUG: balance() called')
    query = update.callback_query
    await query.answer()
    user = query.from_user
    telegram_id = user.id
    print(f'DEBUG: telegram_id={telegram_id}')
    # Fetch balance and full name from the database
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT balance, full_name FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    print(f'DEBUG: db row={row}')
    if row:
        balance = row[0]
        full_name = row[1]
    else:
        balance = 0
        full_name = user.full_name
    message = (
        "💰 <b>Your Balance</b>\n\n"
        f"Current tokens: <b>{balance}</b>\n"
        f"Account: <b>{full_name}</b>\n"
        f"User ID: <b>{telegram_id}</b>"
    )
    keyboard = [
        [InlineKeyboardButton("← Back to Menu", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    print('DEBUG: Sending balance message')
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )