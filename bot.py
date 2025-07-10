from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime, timedelta
import requests
import json

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
MERCHANT_API_KEY = os.getenv('OXAPAY_API_KEY')
CALLBACK_URL = os.getenv('OXAPAY_CALLBACK_URL')
RETURN_URL = os.getenv('OXAPAY_RETURN_URL')

conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (telegram_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT, balance INTEGER DEFAULT 0, welcomed INTEGER DEFAULT 0)''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def create_or_get_user(telegram_id, username, full_name):
    try:
        c.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (telegram_id,))
        if not c.fetchone():
            c.execute("INSERT INTO users (telegram_id, username, full_name, welcomed) VALUES (?, ?, ?, 0)", (telegram_id, username, full_name))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

packages = {
    '100': {'tokens': 100, 'amount': 10, 'desc': 'Starter Pack'},
    '250': {'tokens': 250, 'amount': 25, 'desc': 'Basic Pack'},
    '550': {'tokens': 550, 'amount': 55, 'desc': 'Standard Pack'},
    '1000': {'tokens': 1000, 'amount': 100, 'desc': 'Premium Pack'},
    '1500': {'tokens': 1500, 'amount': 155, 'desc': 'Ultimate Pack'}
}

async def start(update, context):
    user = update.message.from_user
    telegram_id = user.id
    username = user.username if user.username else user.first_name
    full_name = user.full_name

    create_or_get_user(telegram_id, username, full_name)

    try:
        c.execute("SELECT welcomed FROM users WHERE telegram_id = ?", (telegram_id,))
        welcomed = c.fetchone()[0]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        welcomed = 0

    welcome_message = "Welcome to TeleKpr! \U0001F389\nYour account has been created automatically.\nYou can start by purchasing tokens to use our services!\n\n\U0001F4B0 Your current balance: 0 tokens\n\nChoose an option below:"

    keyboard = [
        [InlineKeyboardButton("Buy Tokens", callback_data='buy'), InlineKeyboardButton("New Customer", callback_data='new')],
        [InlineKeyboardButton("My Customers", callback_data='customers'), InlineKeyboardButton("My Orders", callback_data='orders')],
        [InlineKeyboardButton("Marketplace", callback_data='marketplace'), InlineKeyboardButton("Balance", callback_data='balance')],
        [InlineKeyboardButton("Subscribe", callback_data='subscribe'), InlineKeyboardButton("Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if not welcomed:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        try:
            c.execute("UPDATE users SET welcomed = 1 WHERE telegram_id = ?", (telegram_id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
    else:
        balance_message = "Welcome back to TeleKpr! \U0001F389\nYour current balance: 0 tokens\n\nChoose an option below:"
        await update.message.reply_text(balance_message, reply_markup=reply_markup)

async def buy_tokens(update, context):
    query = update.callback_query
    await query.answer()

    buy_message = "Choose a token package:"
    keyboard = [[InlineKeyboardButton(f"{pkg['tokens']} tokens - ${pkg['amount']}", callback_data=key)] for key, pkg in packages.items()]
    keyboard.append([InlineKeyboardButton("\U0001F4B0 Custom Amount", callback_data='custom')])
    keyboard.append([InlineKeyboardButton("\u2190 Back to Menu", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=buy_message, reply_markup=reply_markup)

async def create_payment(update, context):
    query = update.callback_query
    await query.answer()
    package = query.data
    user = query.from_user

    if package in packages:
        pkg = packages[package]
        order_id = f"{user.id}_{package}"

        invoice_data = {
            "amount": pkg['amount'],
            "currency": "USD",
            "lifetime": 30,
            "to_currency": "USDT",
            "fee_paid_by_payer": 1,
            "mixed_payment": True,
            "callback_url": CALLBACK_URL,
            "return_url": RETURN_URL,
            "order_id": order_id,
            "description": f"{pkg['desc']} for {user.username or user.first_name}",
            "sandbox": False
        }

        headers = {
            'merchant_api_key': MERCHANT_API_KEY,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post("https://api.oxapay.com/v1/payment/invoice", json=invoice_data, headers=headers)
            if response.status_code == 200:
                result = response.json()['data']
                payment_message = (f"\U0001F4B3 Payment Created!\n"
                                   f"Package: {pkg['tokens']} tokens\n"
                                   f"Amount: ${pkg['amount']} USD\n"
                                   f"Description: {pkg['desc']}\n"
                                   f"Click \"Pay Now\" to complete your payment.\n"
                                   f"This invoice expires in 30 minutes.")
                keyboard = [[InlineKeyboardButton("Pay Now", url=result['payment_url'])], [InlineKeyboardButton("\u2190 Back to Menu", callback_data='back')]]
                await query.edit_message_text(text=payment_message, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await query.edit_message_text(text="❌ Failed to create payment. Please try again later.")
        except Exception as e:
            await query.edit_message_text(text=f"❌ Error creating payment: {e}")

    elif package == 'custom':
        await query.edit_message_text(text="Please specify your custom amount! (e.g., /custom 200 20)",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("\u2190 Back to Menu", callback_data='back')]]))

    elif package == 'back':
        await start(update, context)

    else:
        await query.edit_message_text(text="Option not recognized!")

async def button(update, context):
    query = update.callback_query
    await query.answer()
    option = query.data

    if option == 'buy':
        await buy_tokens(update, context)
    elif option in list(packages.keys()) + ['custom', 'back']:
        await create_payment(update, context)
    else:
        responses = {
            'new': 'You selected New Customer!',
            'customers': 'You selected My Customers!',
            'orders': 'You selected My Orders!',
            'marketplace': 'You selected Marketplace!',
            'balance': 'Your current balance: 0 tokens',
            'subscribe': 'You selected Subscribe!',
            'help': 'Need help? Contact support!'
        }
        await query.edit_message_text(text=responses.get(option, "Option not recognized!"))

def main():
    init_db()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()
    conn.close()

if __name__ == '__main__':
    main()
