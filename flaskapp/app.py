# app.py
from flask import Flask, request
import sqlite3
import requests
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN')

def send_telegram_message(telegram_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": telegram_id,
        "text": message
    }
    requests.post(url, data=data)

@app.route('/')
def home():
    return '✅ Flask is running'

@app.route('/oxapay_callback', methods=['POST'])
def oxapay_callback():
    data = request.json
    print("📥 Callback received from Oxapay:", data)
    order_id = data.get('order_id')  # e.g., "123456789_250"
    payment_id = data.get('payment_id') or data.get('track_id')
    status = data.get('status')

    # Only process if payment is successful
    if not order_id or not payment_id or status.lower() != 'paid':
        return 'Invalid or unpaid', 400

    # Parse telegram_id and tokens from order_id
    try:
        telegram_id, tokens = order_id.split('_')
        telegram_id = int(telegram_id)
        tokens = int(tokens)
    except Exception as e:
        print("Order ID parse error:", e)
        return 'Order ID error', 400

    # Update user balance (create user if not exists)
    conn = sqlite3.connect('../users.db', check_same_thread=False)
    c = conn.cursor()

    # Check if user exists
    c.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    if row is None:
        # User does not exist, create user with default values
        c.execute("INSERT INTO users (telegram_id, username, full_name, balance, welcomed) VALUES (?, ?, ?, 0, 0)", (telegram_id, '', '',))
        conn.commit()

    # Now update balance
    c.execute("UPDATE users SET balance = balance + ? WHERE telegram_id = ?", (tokens, telegram_id))
    conn.commit()
    c.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    new_balance = c.fetchone()[0]
    conn.close()

    # Send confirmation message
    message = (
        "🎉 Payment Processed Successfully!\n\n"
        f"💰 {tokens} tokens have been added to your account\n\n"
        f"📊 New Balance: {new_balance} tokens\n\n"
        f"💳 Payment ID: {payment_id}\n\n"
        "✨ Your payment was processed by our backup system to ensure you receive your tokens promptly.\n\n"
        "---\n"
        "🤖 PrBot_Pay CRM System"
    )
    send_telegram_message(telegram_id, message)
    return 'OK', 200

if __name__ == '__main__':
    app.run(port=5000)
