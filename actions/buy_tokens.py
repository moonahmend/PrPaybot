from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import os
import requests
from dotenv import load_dotenv
import sqlite3

load_dotenv()
MERCHANT_API_KEY = os.getenv('OXAPAY_API_KEY')
CALLBACK_URL = os.getenv('OXAPAY_CALLBACK_URL')
RETURN_URL = os.getenv('OXAPAY_RETURN_URL')

TOKEN_PACKAGES = [
    {"tokens": 100, "price": 12},
    {"tokens": 250, "price": 27},
    {"tokens": 550, "price": 52},
    {"tokens": 1000, "price": 97},
    {"tokens": 1500, "price": 152},
]

async def buy_tokens(update, context):
    query = update.callback_query
    user = query.from_user
    telegram_id = user.id

    # Remove profile check: allow all users to buy tokens
    await query.answer()
    message = (
        "💳 <b>Buy Tokens</b>\n\n"
        "Select a token package to purchase:"
    )
    keyboard = []
    for package in TOKEN_PACKAGES:
        label = f"💰 {package['tokens']} tokens (${package['price']})"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"buy_{package['tokens']}")])
    keyboard.append([InlineKeyboardButton("💎 Custom Amount", callback_data="custom_token")])
    keyboard.append([InlineKeyboardButton("← Back to Menu", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def custom_token_purchase(update, context):
    query = update.callback_query
    await query.answer()
    message = (
        "💰 <b>Custom Token Purchase</b>\n\n"
        "Enter the number of tokens you want to buy:\n\n"
        "• Rate: $0.10 per token\n"
        "• Minimum: 100 tokens ($10.00)\n\n"
        "Please enter token amount (example: 100, 250, 500, 1000):"
    )
    keyboard = [
        [InlineKeyboardButton("← Back to Tokens", callback_data='buy')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    context.user_data['awaiting_custom_token'] = True
    context.user_data['custom_token_mode'] = 'by_token'

async def handle_text(update, context):
    if context.user_data.get('awaiting_custom_token') and context.user_data.get('custom_token_mode') == 'by_token':
        text = update.message.text.strip()
        try:
            tokens = int(text)
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid token amount (e.g., 100, 250, 500, 1000).")
            return
        if tokens < 100:
            await update.message.reply_text("❌ Minimum purchase is 100 tokens ($10.00). Please enter a higher amount.")
            return
        amount = tokens * 0.10
        user = update.message.from_user
        order_id = f"{user.id}_{tokens}"
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
            "description": f"Custom Token Purchase for {user.username or user.first_name}",
            "sandbox": False  # Set to False in production
        }
        headers = {
            'merchant_api_key': MERCHANT_API_KEY,
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post("https://api.oxapay.com/v1/payment/invoice", json=invoice_data, headers=headers)
            if response.status_code == 200:
                result = response.json()['data']
                message = (
                    f"💳 <b>Confirm Purchase</b>\n\n"
                    f"Tokens: <b>{tokens}</b>\n"
                    f"Amount: <b>${amount:.2f}</b>\n\n"
                    f"Click 💸 Pay Now to complete your purchase."
                )
                keyboard = [
                    [InlineKeyboardButton("💸 Pay Now", url=result['payment_url'])],
                    [InlineKeyboardButton("← Back to Tokens", callback_data='buy')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text("❌ Failed to create payment. Please try again later.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error creating payment: {e}")
        context.user_data['awaiting_custom_token'] = False
        context.user_data['custom_token_mode'] = None
    else:
        await handle_text(update, context)
