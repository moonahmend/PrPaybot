from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import sqlite3
import threading
from flask import Flask, request
import requests
import datetime

# Import admin app
from flaskapp.admin_app import app as admin_app

# Load environment variables from .env file
load_dotenv()

# Get the bot token from the environment
TOKEN = os.getenv('BOT_TOKEN')

# Use Railway's PORT environment variable or default to 5000
PORT = int(os.getenv('PORT', 5000))

# Global database connection - use absolute path for Railway
DB_PATH = os.path.abspath('users.db')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

def ensure_customer_profiles_schema():
    DB_PATH = 'users.db'
    REQUIRED_COLUMNS = [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("telegram_id", "INTEGER"),
        ("profile_number", "INTEGER"),
        ("first_name", "TEXT"),
        ("middle_name", "TEXT"),
        ("last_name", "TEXT"),
        ("email", "TEXT"),
        ("phone_number", "TEXT"),
        ("address_line_1", "TEXT"),
        ("address_line_2", "TEXT"),
        ("city", "TEXT"),
        ("state", "TEXT"),
        ("postal_code", "TEXT"),
        ("country", "TEXT"),
        ("date_of_birth", "TEXT"),
        ("gender", "TEXT"),
        ("identification_number", "TEXT"),
        ("preferred_contact_method", "TEXT"),
        ("password", "TEXT"),
        ("profile_id", "TEXT"),
        ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
    ]
    def column_exists(cursor, table, column):
        cursor.execute(f"PRAGMA table_info({table})")
        return any(row[1] == column for row in cursor.fetchall())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"""
    CREATE TABLE IF NOT EXISTS customer_profiles (
        {', '.join([f'{col} {coltype}' for col, coltype in REQUIRED_COLUMNS])}
    )
    """)
    for col, coltype in REQUIRED_COLUMNS:
        if not column_exists(c, 'customer_profiles', col):
            c.execute(f"ALTER TABLE customer_profiles ADD COLUMN {col} {coltype}")
    conn.commit()
    conn.close()

# Call the schema ensure function at the top of the file
ensure_customer_profiles_schema()

# Initialize or connect to SQLite database
def init_db():
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (telegram_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT, balance INTEGER DEFAULT 0, welcomed INTEGER DEFAULT 0, subscription_active INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS orders
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, order_type TEXT, details TEXT, amount INTEGER, created_at TEXT, status TEXT DEFAULT 'completed')''')
        c.execute('''CREATE TABLE IF NOT EXISTS customer_profiles
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, profile_number INTEGER, first_name TEXT, last_name TEXT, email TEXT, phone_number TEXT, address_line_1 TEXT, address_line_2 TEXT, city TEXT, state TEXT, postal_code TEXT, country TEXT, date_of_birth TEXT, gender TEXT, identification_number TEXT, preferred_contact_method TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Check if user exists and create account if not, set welcomed flag
def create_or_get_user(telegram_id, username, full_name):
    try:
        c.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (telegram_id,))
        if not c.fetchone():
            c.execute("INSERT INTO users (telegram_id, username, full_name, welcomed) VALUES (?, ?, ?, 0)", (telegram_id, username, full_name))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

async def start(update, context):
    user = update.message.from_user
    telegram_id = user.id
    username = user.username if user.username else user.first_name
    full_name = user.full_name
    
    # Create or get user account
    create_or_get_user(telegram_id, username, full_name)
    
    try:
        c.execute("SELECT welcomed, balance FROM users WHERE telegram_id = ?", (telegram_id,))
        result = c.fetchone()
        welcomed = result[0] if result else 0
        user_balance = result[1] if result else 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        welcomed = 0
        user_balance = 0

    welcome_message = f"Welcome to PrBot_Pay, {full_name}! 🎉\n \nYour account has been created automatically.\nYou can start by purchasing tokens to use our services!\n\n💰 Your current balance: {user_balance} tokens\n\nChoose an option below:"

    keyboard = [
        [InlineKeyboardButton("💰 Buy Tokens", callback_data='buy'), InlineKeyboardButton("🧑‍💼 New Customer", callback_data='new')],
        [InlineKeyboardButton("👥 My Customers", callback_data='customers'), InlineKeyboardButton("📦 My Orders", callback_data='orders')],
        [InlineKeyboardButton("🛒 Marketplace", callback_data='marketplace'), InlineKeyboardButton("💳 Balance", callback_data='balance')],
        [InlineKeyboardButton("🏷️ Subscribe", callback_data='subscribe'), InlineKeyboardButton("❓ Help", callback_data='help')]
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
        balance_message = f"Welcome back to PrBot_Pay, {full_name}! 🎉\nYour current balance: {user_balance} tokens\n\nChoose an option below:"
        await update.message.reply_text(balance_message, reply_markup=reply_markup)

# Import action modules
from actions.buy_tokens import buy_tokens, custom_token_purchase, handle_text as buy_tokens_handle_text
from actions.create_payment import create_payment, create_payment_with_amount
from actions.back_to_menu import back_to_menu
from actions.new_customer import new_customer, handle_text, button as new_customer_button
from actions.subscribe import subscribe_button
from actions.my_customers import my_customers, view_customer_profile
from actions.my_orders import my_orders
from actions.marketplace import marketplace, handle_marketplace_order, show_subscription_packages, handle_subscription_package_order
from actions.balance import balance
from actions.help import help

async def button(update, context):
    query = update.callback_query
    option = query.data

    # Route subscription plan callbacks
    if option in ['sub_standard', 'sub_gold', 'sub_plus', 'sub_platinum']:
        await subscribe_button(update, context)
        return
    
    # Route custom token purchase
    if option == 'custom_token':
        await custom_token_purchase(update, context)
        return
    
    # Route token package purchases (buy_100, buy_250, etc.)
    if option.startswith('buy_'):
        # Extract the token amount from buy_100 -> 100
        token_amount = option.split('_')[1]
        # Call create_payment with the token amount
        await create_payment_with_amount(update, context, token_amount)
        return
    
    # Handle view specific customer profile
    if option.startswith('view_profile_'):
        profile_number = int(option.split('_')[2])
        await view_customer_profile(update, context, profile_number)
        return
    
    # Handle edit specific customer profile
    if option.startswith('edit_profile_'):
        profile_number = int(option.split('_')[2])
        await query.edit_message_text(
            text=f"📝 <b>Edit Profile #{profile_number}</b>\n\nPlease enter the field name you want to edit:\n\nAvailable fields: first_name, last_name, email, phone_number, address_line_1, address_line_2, city, state, postal_code, country, date_of_birth, gender, identification_number, preferred_contact_method",
            parse_mode='HTML'
        )
        context.user_data['editing_profile'] = profile_number
        context.user_data['editing'] = True
        return
    
    # Handle delete specific customer profile
    if option.startswith('delete_profile_'):
        profile_number = int(option.split('_')[2])
        keyboard = [
            [InlineKeyboardButton("✅ Yes, Delete", callback_data=f'confirm_delete_profile_{profile_number}')],
            [InlineKeyboardButton("❌ Cancel", callback_data=f'cancel_delete_profile_{profile_number}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"🗑️ <b>Delete Profile #{profile_number}</b>\n\nAre you sure you want to delete this customer profile?\n\nThis action cannot be undone.",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        context.user_data['deleting_profile'] = profile_number
        return

    # Handle confirm delete specific customer profile
    if option.startswith('confirm_delete_profile_'):
        profile_number = int(option.split('_')[3])
        user = query.from_user
        telegram_id = user.id
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM customer_profiles WHERE telegram_id = ? AND profile_number = ?", (telegram_id, profile_number))
        conn.commit()
        conn.close()
        await query.edit_message_text(
            text=f"✅ <b>Profile #{profile_number} deleted successfully.</b>",
            parse_mode='HTML'
        )
        # Optionally, show the updated customer list
        await my_customers(update, context)
        return

    # Handle cancel delete specific customer profile
    if option.startswith('cancel_delete_profile_'):
        profile_number = int(option.split('_')[3])
        await view_customer_profile(update, context, profile_number)
        return

    # Handle edit profile (general)
    if option == 'edit_profile':
        await query.edit_message_text(
            text="📝 <b>Edit Profile</b>\n\nPlease enter the field name you want to edit:\n\nAvailable fields: first_name, last_name, email, phone_number, address_line_1, address_line_2, city, state, postal_code, country, date_of_birth, gender, identification_number, preferred_contact_method",
            parse_mode='HTML'
        )
        context.user_data['editing'] = True
        return
    
    # Handle Subscription Order and Regular Order buttons
    if option == 'subscription_order':
        await subscribe_button(update, context)
        return
    if option == 'regular_order':
        await marketplace(update, context)
        return
    
    # Handle order for specific customer profile
    if option.startswith('order_for_profile_'):
        profile_number = int(option.split('_')[-1])
        keyboard = [
            [InlineKeyboardButton("Regular Price", callback_data=f'regular_order_for_profile_{profile_number}')],
            [InlineKeyboardButton("Subscription Price", callback_data=f'subscription_order_for_profile_{profile_number}')],
            [InlineKeyboardButton("← Back to Profile", callback_data=f'view_profile_{profile_number}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"<b>Order for Customer Profile #{profile_number}</b>\n\nChoose order type:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return

    # Handle regular/subscription order for selected profile
    if option.startswith('regular_order_for_profile_'):
        profile_number = int(option.split('_')[-1])
        context.user_data['order_profile'] = profile_number
        await marketplace(update, context)
        return
    if option.startswith('subscription_order_for_profile_'):
        profile_number = int(option.split('_')[-1])
        context.user_data['order_profile'] = profile_number
        await subscribe_button(update, context)
        return

    # Handle confirm order
    if option.startswith('confirm_'):
        await handle_marketplace_order(update, context)
        return

    # Only handle actual package selection here
    if option.startswith('order_'):
        await handle_marketplace_order(update, context)
        return
    
    # Marketplace main menu: show Regular/Subscription options
    if option == 'marketplace':
        keyboard = [
            [InlineKeyboardButton("Regular Package", callback_data='regular_package')],
            [InlineKeyboardButton("Subscription Package", callback_data='subscription_package')],
            [InlineKeyboardButton("← Back to Menu", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Choose a package type:",
            reply_markup=reply_markup
        )
        return

    # Regular Package
    if option == 'regular_package':
        await marketplace(update, context)
        return

    # Subscription Package
    if option == 'subscription_package':
        user_id = query.from_user.id
        DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'users.db'))
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT subscription_active FROM users WHERE telegram_id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        if result and result[0]:
            await show_subscription_packages(update, context)
        else:
            await query.edit_message_text(
                text="❌ You need to subscribe first to access subscription packages.\nPlease use the Subscribe button from the main menu.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Subscribe", callback_data='subscribe')],
                    [InlineKeyboardButton("Back to Menu", callback_data='back')]
                ]),
                parse_mode='HTML'
            )
        return

    # Handle subscription package order
    if option.startswith('subpkg_'):
        try:
            sites = int(option.split('_')[1])
            await handle_subscription_package_order(update, context, sites)
        except Exception as e:
            await query.edit_message_text(f"Error processing subscription package: {e}")
        return

    # Route main menu options
    if option == 'buy':
        await buy_tokens(update, context)
    elif option == 'new':
        await new_customer(update, context)
    elif option == 'customers':
        await my_customers(update, context)
    elif option == 'orders':
        await my_orders(update, context)
    elif option == 'balance':
        await balance(update, context)
    elif option == 'subscribe':
        await subscribe_button(update, context)
    elif option == 'help':
        await help(update, context)
    elif option == 'back':
        # Always fetch balance from DB before showing menu
        user = query.from_user
        telegram_id = user.id
        DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'users.db'))
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT full_name, balance FROM users WHERE telegram_id = ?", (telegram_id,))
        row = c.fetchone()
        conn.close()
        full_name = row[0] if row else user.full_name
        user_balance = row[1] if row else 0
        balance_message = f"Welcome back to PrBot_Pay, {full_name}! 🎉\nYour current balance: {user_balance} tokens\n\nChoose an option below:"
        keyboard = [
            [InlineKeyboardButton("💰 Buy Tokens", callback_data='buy'), InlineKeyboardButton("🧑‍💼 New Customer", callback_data='new')],
            [InlineKeyboardButton("👥 My Customers", callback_data='customers'), InlineKeyboardButton("📦 My Orders", callback_data='orders')],
            [InlineKeyboardButton("🛒 Marketplace", callback_data='marketplace'), InlineKeyboardButton("💳 Balance", callback_data='balance')],
            [InlineKeyboardButton("🏷️ Subscribe", callback_data='subscribe'), InlineKeyboardButton("❓ Help", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(balance_message, reply_markup=reply_markup)
        return
    else:
        # Handle other callbacks (like payment packages)
        await new_customer_button(update, context)

async def handle_text_router(update, context):
    if context.user_data.get('awaiting_custom_token'):
        await buy_tokens_handle_text(update, context)
    else:
        await handle_text(update, context)

def send_telegram_message(telegram_id, message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": telegram_id,
        "text": message
    }
    requests.post(url, data=data)

flask_app = Flask(__name__)

# Set secret key for admin sessions
flask_app.secret_key = os.getenv('ADMIN_SECRET_KEY', 'supersecretkey')

# Register admin app routes
flask_app.register_blueprint(admin_app, url_prefix='/admin')

@flask_app.route('/')
def home():
    return '✅ PrBot_Pay is running on Railway!'

@flask_app.route('/admin')
def admin_redirect():
    return '''
    <html>
    <head><title>PrBot_Pay Admin</title></head>
    <body>
        <h1>PrBot_Pay Admin Panel</h1>
        <p><a href="/admin/login">Go to Admin Panel</a></p>
    </body>
    </html>
    '''

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from Telegram"""
    if request.method == 'POST':
        update = request.get_json()
        # Process the update asynchronously
        threading.Thread(target=process_update, args=(update,), daemon=True).start()
        return 'OK', 200
    return 'OK', 200

def process_update(update):
    """Process Telegram update in background thread"""
    try:
        # This is a simplified version - you might want to use the full telegram.ext framework
        # For now, we'll just log the update
        print(f"Received update: {update}")
    except Exception as e:
        print(f"Error processing update: {e}")

@flask_app.route('/set_webhook')
def set_webhook():
    """Set webhook URL for the bot"""
    try:
        webhook_url = request.args.get('url', request.url_root + 'webhook')
        response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            json={'url': webhook_url}
        )
        return f"Webhook set: {response.json()}", 200
    except Exception as e:
        return f"Error setting webhook: {e}", 500

@flask_app.route('/oxapay_callback', methods=['POST'])
def oxapay_callback():
    data = request.json
    print("\U0001F4E5 Callback received from Oxapay:", data)
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
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    if row is None:
        c.execute("INSERT INTO users (telegram_id, username, full_name, balance, welcomed) VALUES (?, ?, ?, 0, 0)", (telegram_id, '', '',))
        conn.commit()
    c.execute("UPDATE users SET balance = balance + ? WHERE telegram_id = ?", (tokens, telegram_id))
    conn.commit()
    c.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    new_balance = c.fetchone()[0]

    # Insert payment record into orders table
    c.execute(
        "INSERT INTO orders (telegram_id, order_type, details, amount, created_at, status) VALUES (?, ?, ?, ?, ?, ?)",
        (telegram_id, 'token_purchase', f'Oxapay payment (Payment ID: {payment_id})', tokens, datetime.datetime.now().isoformat(), 'completed')
    )
    conn.commit()
    conn.close()

    # Send confirmation message
    message = (
        "\U0001F389 Payment Processed Successfully!\n\n"
        f"\U0001F4B0 {tokens} tokens have been added to your account\n\n"
        f"\U0001F4CA New Balance: {new_balance} tokens\n\n"
        f"\U0001F4B3 Payment ID: {payment_id}\n\n"
        "\u2728 Your payment was processed by our backup system to ensure you receive your tokens promptly.\n\n"
        "---\n"
        "\U0001F916 PrBot_Pay CRM System"
    )
    send_telegram_message(telegram_id, message)
    return 'OK', 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=PORT)

def main():
    init_db()  # Initialize database
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_router))
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start the bot
    application.run_polling()
    
    # Close database connection on shutdown
    conn.close()

if __name__ == '__main__':
    main()