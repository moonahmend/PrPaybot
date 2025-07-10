from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def back_to_menu(update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    full_name = user.full_name
    
    balance_message = f"Welcome back to PrBot_Pay, {full_name}! 🎉\nYour current balance: 0 tokens\n\nChoose an option below:"
    keyboard = [
        [InlineKeyboardButton("Buy Tokens       ", callback_data='buy'), InlineKeyboardButton("New Customer     ", callback_data='new')],
        [InlineKeyboardButton("My Customers     ", callback_data='customers'), InlineKeyboardButton("My Orders        ", callback_data='orders')],
        [InlineKeyboardButton("Marketplace      ", callback_data='marketplace'), InlineKeyboardButton("Balance          ", callback_data='balance')],
        [InlineKeyboardButton("Subscribe        ", callback_data='subscribe'), InlineKeyboardButton("Help             ", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(balance_message, reply_markup=reply_markup)