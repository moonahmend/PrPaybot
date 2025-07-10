from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3

async def my_customers(update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    telegram_id = user.id
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create customer_profiles table if not exists
    c.execute("""
    CREATE TABLE IF NOT EXISTS customer_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        profile_number INTEGER,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        phone_number TEXT,
        address_line_1 TEXT,
        address_line_2 TEXT,
        city TEXT,
        state TEXT,
        postal_code TEXT,
        country TEXT,
        date_of_birth TEXT,
        gender TEXT,
        identification_number TEXT,
        preferred_contact_method TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Get all customer profiles for this user
    c.execute("""
        SELECT profile_number, first_name, last_name, email, phone_number, 
               address_line_1, address_line_2, city, state, postal_code, country,
               date_of_birth, gender, identification_number, preferred_contact_method, created_at
        FROM customer_profiles WHERE telegram_id = ? ORDER BY profile_number
    """, (telegram_id,))
    profiles = c.fetchall()
    
    if not profiles:
        # No profiles found
        message = (
            "👥 <b>My Customers</b>\n\n"
            "You haven't created any customer profiles yet.\n"
            "Click \"New Customer\" to create your first profile!"
        )
        keyboard = [
            [InlineKeyboardButton("🧑‍💼 New Customer", callback_data='new')],
            [InlineKeyboardButton("← Back to Menu", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='HTML')
    else:
        # Show list of all customer profiles
        message = f"👥 <b>My Customer Profiles</b>\n\n"
        message += f"📊 <b>Total Profiles:</b> {len(profiles)}\n\n"
        
        # Create buttons for each profile, 3 per row
        profile_buttons = []
        row = []
        for idx, profile in enumerate(profiles):
            (profile_number, first_name, last_name, email, phone_number, 
             address_line_1, address_line_2, city, state, postal_code, country,
             date_of_birth, gender, identification_number, preferred_contact_method, created_at) = profile
            full_name = f"{first_name} {last_name}".strip()
            if not full_name:
                full_name = f"Profile #{profile_number}"
            row.append(InlineKeyboardButton(f"👤 View #{profile_number} - {full_name}", callback_data=f'view_profile_{profile_number}'))
            if (idx + 1) % 3 == 0:
                profile_buttons.append(row)
                row = []
        if row:
            profile_buttons.append(row)
        # Add action buttons
        profile_buttons.append([InlineKeyboardButton("🧑‍💼 Add New Customer", callback_data='new')])
        profile_buttons.append([InlineKeyboardButton("← Back to Menu", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(profile_buttons)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='HTML')
    
    conn.close()

async def view_customer_profile(update, context, profile_number):
    """Display detailed information for a specific customer profile"""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    telegram_id = user.id
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    
    # Get specific profile details
    c.execute("""
        SELECT profile_number, first_name, last_name, email, phone_number, 
               address_line_1, address_line_2, city, state, postal_code, country,
               date_of_birth, gender, identification_number, preferred_contact_method, created_at
        FROM customer_profiles WHERE telegram_id = ? AND profile_number = ?
    """, (telegram_id, profile_number))
    profile = c.fetchone()
    
    if not profile:
        await query.edit_message_text(
            text="❌ Profile not found!",
            parse_mode='HTML'
        )
        conn.close()
        return
    
    (profile_number, first_name, last_name, email, phone_number, 
     address_line_1, address_line_2, city, state, postal_code, country,
     date_of_birth, gender, identification_number, preferred_contact_method, created_at) = profile
    
    # Build complete profile message
    message = f"👤 <b>Customer Profile #{profile_number}</b>\n\n"
    
    # Personal Information
    message += f"📋 <b>Personal Information:</b>\n"
    if first_name or last_name:
        full_name = f"{first_name} {last_name}".strip()
        message += f"• Full Name: <b>{full_name}</b>\n"
    if email:
        message += f"• Email: <b>{email}</b>\n"
    if phone_number:
        message += f"• Phone: <b>{phone_number}</b>\n"
    if date_of_birth:
        message += f"• Date of Birth: <b>{date_of_birth}</b>\n"
    if gender:
        message += f"• Gender: <b>{gender}</b>\n"
    if identification_number:
        message += f"• ID Number: <b>{identification_number}</b>\n"
    if preferred_contact_method:
        message += f"• Contact Method: <b>{preferred_contact_method}</b>\n"
    
    # Address Information
    message += f"\n🏠 <b>Address Information:</b>\n"
    if address_line_1:
        message += f"• Address Line 1: <b>{address_line_1}</b>\n"
    if address_line_2:
        message += f"• Address Line 2: <b>{address_line_2}</b>\n"
    if city:
        message += f"• City: <b>{city}</b>\n"
    if state:
        message += f"• State: <b>{state}</b>\n"
    if postal_code:
        message += f"• ZIP Code: <b>{postal_code}</b>\n"
    if country:
        message += f"• Country: <b>{country}</b>\n"
    
    # Profile Information
    message += f"\n📅 <b>Profile Information:</b>\n"
    message += f"• Profile Number: <b>#{profile_number}</b>\n"
    if created_at:
        message += f"• Created: <b>{created_at[:19].replace('T', ' ')}</b>\n"
    message += f"• Status: <b>Active</b>"
    
    keyboard = [
        [InlineKeyboardButton("🛒 Order for this Customer", callback_data=f'order_for_profile_{profile_number}')],
        [InlineKeyboardButton("✏️ Edit Profile", callback_data=f'edit_profile_{profile_number}')],
        [InlineKeyboardButton("🗑️ Delete Profile", callback_data=f'delete_profile_{profile_number}')],
        [InlineKeyboardButton("👥 Back to All Customers", callback_data='customers')],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='HTML')
    
    conn.close()

# Add this handler for order_for_profile_X
async def button(update, context):
    query = update.callback_query
    option = query.data
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