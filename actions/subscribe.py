from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3
import datetime
import os
import requests
from dotenv import load_dotenv

load_dotenv()
MERCHANT_API_KEY = os.getenv('OXAPAY_API_KEY')
CALLBACK_URL = os.getenv('OXAPAY_CALLBACK_URL')
RETURN_URL = os.getenv('OXAPAY_RETURN_URL')

SUBSCRIPTION_PLANS = {
    'sub_standard': {'name': 'Standard', 'price': 45},
    'sub_gold': {'name': 'Gold', 'price': 72},
    'sub_plus': {'name': 'Plus', 'price': 95},
    'sub_platinum': {'name': 'Platinum', 'price': 145},
}

def get_plan_tokens(plan):
    return int(plan['price'] * 10)

def get_plan_label(plan):
    return f"🏷️ {plan['name']} - {get_plan_tokens(plan)} tokens (${plan['price']})"

async def subscribe(update, context):
    query = update.callback_query
    await query.answer()
    message = (
        "\U0001F3AF <b>Premium Subscription</b>\n\n"
        "\U0001F4A1 No active subscription\n\n"
        "\u2728 <b>Benefits of Premium Subscription:</b>\n"
        "• Discounted prices\n"
        "• Priority\n\n"
        "\U0001F4B0 <b>Choose a subscription plan:</b>"
    )
    keyboard = []
    for key, plan in SUBSCRIPTION_PLANS.items():
        label = get_plan_label(plan)
        keyboard.append([InlineKeyboardButton(label, callback_data=key)])
    keyboard.append([InlineKeyboardButton("← Back to Menu", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def subscribe_button(update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    telegram_id = user.id
    plan_key = query.data
    if plan_key not in SUBSCRIPTION_PLANS:
        await subscribe(update, context)
        return
    plan = SUBSCRIPTION_PLANS[plan_key]
    tokens = get_plan_tokens(plan)
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            order_type TEXT,
            details TEXT,
            amount INTEGER,
            created_at TEXT
        )
    """)
    c.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    balance = row[0] if row else 0
    if balance >= tokens:
        c.execute("UPDATE users SET balance = balance - ? WHERE telegram_id = ?", (tokens, telegram_id))
        c.execute(
            "INSERT INTO orders (telegram_id, order_type, details, amount, created_at) VALUES (?, ?, ?, ?, ?)",
            (telegram_id, "subscription", plan['name'], tokens, datetime.datetime.now().isoformat())
        )
        c.execute("UPDATE users SET subscription_active = 1 WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        conn.close()
        message = (
            f"\u2705 <b>Subscription Activated!</b>\n\n"
            f"Plan: <b>{plan['name']}</b>\n"
            f"You have successfully subscribed.\n"
            f"Your new balance: <b>{balance - tokens}</b> tokens"
        )
        keyboard = [
            [InlineKeyboardButton("← Back to Menu", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='HTML')
    else:
        need = tokens - balance
        # Create payment invoice (simulate payment URL for now)
        amount = plan['price']
        order_id = f"{telegram_id}_sub_{plan['name']}"
        invoice_data = {
            "amount": amount,
            "currency": "USD",
            "lifetime": 30,
            "to_currency": "USDT",
            "fee_paid_by_payer": 1,
            "mixed_payment": True,
            "callback_url": CALLBACK_URL,
            "return_url": RETURN_URL,
            "order_id": order_id,
            "description": f"Subscription Purchase: {plan['name']}",
            "sandbox": False  # Set to False in production
        }
        headers = {
            'merchant_api_key': MERCHANT_API_KEY,
            'Content-Type': 'application/json'
        }
        payment_url = None
        try:
            response = requests.post("https://api.oxapay.com/v1/payment/invoice", json=invoice_data, headers=headers)
            if response.status_code == 200:
                result = response.json()['data']
                payment_url = result['payment_url']
        except Exception as e:
            payment_url = None
        message = (
            f"\u274c <b>Insufficient Tokens</b>\n\n"
            f"Plan: <b>{plan['name']}</b>\n"
            f"Required: <b>{tokens} tokens</b>\n"
            f"Your balance: <b>{balance} tokens</b>\n"
            f"Need <b>{need} more tokens</b>\n\n"
            f"You can pay directly for this subscription:"
        )
        keyboard = []
        if payment_url:
            keyboard.append([InlineKeyboardButton("💸 Pay Now", url=payment_url)])
        keyboard.append([InlineKeyboardButton("💳 Buy Tokens", callback_data='buy')])
        keyboard.append([InlineKeyboardButton("← Back to Menu", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='HTML')