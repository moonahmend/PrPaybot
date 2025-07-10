import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

load_dotenv()
MERCHANT_API_KEY = os.getenv('OXAPAY_API_KEY')
CALLBACK_URL = os.getenv('OXAPAY_CALLBACK_URL')
RETURN_URL = os.getenv('OXAPAY_RETURN_URL')

packages = {
    '100': {'tokens': 100, 'amount': 10, 'desc': 'Starter Pack'},
    '250': {'tokens': 250, 'amount': 25, 'desc': 'Basic Pack'},
    '550': {'tokens': 550, 'amount': 55, 'desc': 'Standard Pack'},
    '1000': {'tokens': 1000, 'amount': 100, 'desc': 'Premium Pack'},
    '1500': {'tokens': 1500, 'amount': 155, 'desc': 'Ultimate Pack'}
}

async def create_payment(update, context):
    query = update.callback_query
    await query.answer()
    package = query.data
    user = query.from_user

    if package in packages:
        pkg = packages[package]
        order_id = f"{user.id}_{pkg['tokens']}"
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
        from actions.back_to_menu import back_to_menu
        await back_to_menu(update, context)
    else:
        await query.edit_message_text(text="Option not recognized!")

async def create_payment_with_amount(update, context, token_amount):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if token_amount in packages:
        pkg = packages[token_amount]
        order_id = f"{user.id}_{pkg['tokens']}"
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
    else:
        await query.edit_message_text(text="Option not recognized!")