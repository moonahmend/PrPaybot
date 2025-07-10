from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def help(update, context):
    query = update.callback_query
    await query.answer()
    message = (
        "❓ <b>PrBot_Pay Help</b>\n\n"
        "🔷 <b>Buy Tokens:</b> Purchase tokens to use our services\n"
        "🔷 <b>New Customer:</b> Register a new customer profile\n"
        "🔷 <b>My Customers:</b> View and manage your registered customers\n"
        "🔷 <b>My Orders:</b> View your order history and status\n"
        "🔷 <b>Marketplace:</b> Browse and order registration packages\n"
        "🔷 <b>Balance:</b> Check your current token balance\n\n"
        "💡 Need more help? Contact support."
    )
    keyboard = [
        [InlineKeyboardButton("← Back to Menu", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )