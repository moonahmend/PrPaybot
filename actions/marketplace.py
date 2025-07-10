import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Package definitions: (sites, callback, usd_price)
MARKETPLACE_PACKAGES = [
    ("250 Sites $25", "order_250", 25),
    ("550 Sites $50", "order_550", 50),
    ("750 Sites $75", "order_750", 75),
    ("850 Sites $85", "order_850", 85),
    ("1000 Sites $95", "order_1000", 95),
    ("1225 Sites $120", "order_1225", 120),
    ("1350 Sites $130", "order_1350", 130),
    ("1500 Sites $150", "order_1500", 150),
    ("1700 Sites $170", "order_1700", 170),
    ("1825 Sites $180", "order_1825", 180),
    ("2000 Sites $200", "order_2000", 200),
    ("2500 Sites $250", "order_2500", 250),
    ("3000 Sites $299", "order_3000", 299),
]

SUBSCRIPTION_PACKAGES = [
    {"sites": 250, "price": 15},
    {"sites": 550, "price": 45},
    {"sites": 750, "price": 65},
    {"sites": 850, "price": 70},
    {"sites": 1000, "price": 80},
    {"sites": 1225, "price": 100},
    {"sites": 1350, "price": 115},
    {"sites": 1500, "price": 135},
    {"sites": 1700, "price": 145},
    {"sites": 1825, "price": 165},
    {"sites": 2000, "price": 189},
    {"sites": 2500, "price": 220},
    {"sites": 3000, "price": 279},
]

async def marketplace(update, context):
    query = update.callback_query
    await query.answer()
    message = (
        "🛒 <b>Marketplace</b>\n\n"
        "<b>💵 REGULAR PRICE!</b> 🛍️\n\n"
        "Select a package below to order:"
    )
    profile_number = context.user_data.get('order_profile')
    print("DEBUG: marketplace profile_number =", profile_number)
    keyboard = []
    for text, cb, usd_price in MARKETPLACE_PACKAGES:
        keyboard.append([InlineKeyboardButton(f"🛍️ {text}", callback_data=cb)])
    print("DEBUG: marketplace keyboard =", [btn[0].callback_data for btn in keyboard])
    keyboard.append([InlineKeyboardButton("← Back to Menu", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def handle_marketplace_order(update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    telegram_id = user.id
    selected_cb = query.data
    profile_number = None
    if selected_cb.startswith('confirm_'):
        confirm_cb = selected_cb[len('confirm_'):]
        if '_for_profile_' in confirm_cb:
            cb_base, profile_number = confirm_cb.rsplit('_for_profile_', 1)
            selected_cb = cb_base
            try:
                profile_number = int(profile_number)
            except Exception:
                profile_number = None
        else:
            selected_cb = confirm_cb
        for text, cb, usd_price in MARKETPLACE_PACKAGES:
            if cb == selected_cb:
                package_text = text
                break
        else:
            await query.edit_message_text("\u274c Invalid package selected.")
            return
        required_tokens = int(usd_price * 10)
        conn = sqlite3.connect('users.db', check_same_thread=False)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, order_type TEXT, details TEXT, amount INTEGER, created_at TEXT)")
        c.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
        row = c.fetchone()
        balance = row[0] if row else 0
        if balance < required_tokens:
            await query.edit_message_text("❌ Insufficient tokens for this order.")
            conn.close()
            return
        c.execute("UPDATE users SET balance = balance - ? WHERE telegram_id = ?", (required_tokens, telegram_id))
        import datetime
        c.execute(
            "INSERT INTO orders (telegram_id, order_type, details, amount, created_at) VALUES (?, ?, ?, ?, ?)",
            (telegram_id, "marketplace", package_text, required_tokens, datetime.datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        message = (
            f"✅ <b>Order Placed Successfully!</b>\n\n"
            f"Order: <b>{package_text}</b>\n"
            f"Tokens deducted: <b>{required_tokens}</b>\n"
            f"New balance: <b>{balance - required_tokens}</b>\n\n"
        )
        if profile_number:
            message += f"For Customer Profile: <b>#{profile_number}</b>\n"
        message += "🎉 Thank you for your order!"
        keyboard = [[InlineKeyboardButton("← Back to Marketplace", callback_data='marketplace')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='HTML')
        return
    if '_for_profile_' in selected_cb:
        cb_base, profile_number = selected_cb.rsplit('_for_profile_', 1)
        selected_cb = cb_base
        try:
            profile_number = int(profile_number)
        except Exception:
            profile_number = None
        context.user_data['order_profile'] = profile_number
    else:
        profile_number = context.user_data.get('order_profile')
    print("DEBUG: selected_cb =", selected_cb, "profile_number =", profile_number)
    print("DEBUG: MARKETPLACE_PACKAGES =", [cb for _, cb, _ in MARKETPLACE_PACKAGES])
    for text, cb, usd_price in MARKETPLACE_PACKAGES:
        if cb == selected_cb:
            package_text = text
            break
    else:
        await query.edit_message_text("\u274c Invalid package selected.")
        return
    required_tokens = int(usd_price * 10)
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    balance = row[0] if row else 0
    conn.close()
    if balance >= required_tokens:
        message = (
            f"✅ <b>Order Confirmation</b>\n\n"
            f"You are about to order: <b>{package_text}</b>\n"
            f"This will deduct <b>{required_tokens} tokens</b> from your balance.\n\n"
            f"Do you want to proceed?"
        )
        keyboard = [
            [InlineKeyboardButton("✅ Confirm Order", callback_data=f'confirm_{selected_cb}')],
            [InlineKeyboardButton("← Back to Marketplace", callback_data='marketplace')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='HTML')
    else:
        message = (
            f"⚠️ <b>Insufficient Tokens</b>\n\n"
            f"You selected: <b>{package_text}</b>\n"
            f"Required: <b>{required_tokens} tokens</b>\n"
            f"Your balance: <b>{balance} tokens</b>\n\n"
            f"You do not have enough tokens to place this order.\n"
            f"Please buy more tokens or subscribe."
        )
        keyboard = [
            [InlineKeyboardButton("💳 Buy Token", callback_data='buy')],
            [InlineKeyboardButton("✨ Subscribe", callback_data='subscribe')],
            [InlineKeyboardButton("← Back to Marketplace", callback_data='marketplace')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='HTML')

async def show_subscription_packages(update, context):
    query = update.callback_query
    keyboard = []
    for pkg in SUBSCRIPTION_PACKAGES:
        label = f"🛍️ {pkg['sites']} Sites ${pkg['price']}"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"subpkg_{pkg['sites']}")])
    keyboard.append([InlineKeyboardButton("← Back", callback_data='marketplace')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="<b>✨ SUBSCRIPTION PRICE!</b> 🛍️\nChoose your subscription package:",
        reply_markup=reply_markup
    )

async def handle_subscription_package_order(update, context, sites):
    query = update.callback_query
    user = query.from_user
    telegram_id = user.id
    # Find the selected package
    pkg = next((p for p in SUBSCRIPTION_PACKAGES if p['sites'] == sites), None)
    if not pkg:
        await query.edit_message_text("\u274c Invalid subscription package selected.")
        return
    price = pkg['price']
    required_tokens = int(price * 10)
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT balance, subscription_active FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        await query.edit_message_text("\u274c User not found.")
        return
    balance, subscription_active = row
    if not subscription_active:
        conn.close()
        await query.edit_message_text("\u274c You need an active subscription to order these packages.")
        return
    if balance < required_tokens:
        conn.close()
        await query.edit_message_text(f"⚠️ <b>Insufficient Tokens</b>\n\nRequired: <b>{required_tokens} tokens</b>\nYour balance: <b>{balance} tokens</b>", parse_mode='HTML')
        return
    # Deduct tokens and insert order
    import datetime
    c.execute("UPDATE users SET balance = balance - ? WHERE telegram_id = ?", (required_tokens, telegram_id))
    c.execute(
        "INSERT INTO orders (telegram_id, order_type, details, amount, created_at, status) VALUES (?, ?, ?, ?, ?, ?)",
        (telegram_id, "subscription_package", f"{sites} Sites", required_tokens, datetime.datetime.now().isoformat(), 'completed')
    )
    conn.commit()
    c.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    new_balance = c.fetchone()[0]
    conn.close()
    message = (
        f"✅ <b>Order Placed Successfully!</b>\n\n"
        f"Subscription Package: <b>{sites} Sites</b>\n"
        f"Tokens deducted: <b>{required_tokens}</b>\n"
        f"New balance: <b>{new_balance}</b>\n\n"
        "Thank you for your order!"
    )
    keyboard = [[InlineKeyboardButton("← Back to Marketplace", callback_data='marketplace')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='HTML')