# PrBot_Pay - Telegram Bot with Admin Panel

A comprehensive Telegram bot with payment processing and admin panel for managing users, orders, and payments.

## Features

- 🤖 Telegram Bot with interactive menus
- 💳 Payment processing via Oxapay
- 👥 Customer profile management
- 🛒 Marketplace with subscription packages
- 📊 Admin panel for user and order management
- 💰 Token-based system
- 🔐 Secure admin authentication

## Quick Start

### 1. Generate Secret Keys

Before deployment, generate secure secret keys:

```bash
# Generate a single secret key
python generate_secret.py

# Generate multiple keys
python generate_secret.py --count 5

# Generate different types of keys
python generate_secret.py --type hex
python generate_secret.py --type custom
```

Or use the Windows batch file:
```cmd
generate_secret.bat
```

### 2. Set Environment Variables

Copy the generated keys and set them in Railway:

```
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_SECRET_KEY=your_generated_secret_key_here
```

## Railway Deployment

### Prerequisites

1. **Telegram Bot Token**: Get from [@BotFather](https://t.me/botfather)
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **GitHub Account**: For code repository

### Step 1: Prepare Your Code

1. Fork or clone this repository
2. Make sure all files are in the root directory
3. Generate secret keys using the provided script
4. Ensure your `.env` file has the required variables (see `env.example`)

### Step 2: Deploy to Railway

1. **Login to Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign in with your GitHub account

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Environment Variables**:
   - Go to your project settings
   - Add the following environment variables:
     ```
     BOT_TOKEN=your_telegram_bot_token_here
     ADMIN_SECRET_KEY=your_secure_secret_key_here
     ```

4. **Deploy**:
   - Railway will automatically detect the Python project
   - It will use the `Procfile` to start the application
   - The bot and admin panel will be available at your Railway URL

### Step 3: Access Your Application

- **Main Bot**: Your Railway URL (e.g., `https://your-app.railway.app`)
- **Admin Panel**: `https://your-app.railway.app/admin`
- **Admin Login**: 
  - Username: `admin`
  - Password: `admin123` (change this in production!)

### Step 4: Configure Webhook (Optional)

If you want to use webhooks instead of polling:

1. Set your bot's webhook URL:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-app.railway.app/webhook
   ```

2. Add webhook route to your bot (modify `main.py`)

## File Structure

```
├── main.py                 # Main bot and Flask app
├── requirements.txt        # Python dependencies
├── Procfile              # Railway deployment config
├── runtime.txt           # Python version
├── env.example           # Environment variables template
├── generate_secret.py    # Secret key generator script
├── generate_secret.bat   # Windows batch file for key generation
├── flaskapp/
│   ├── admin_app.py      # Admin panel Blueprint
│   └── app.py           # Backup Flask app
├── actions/              # Bot action modules
│   ├── buy_tokens.py
│   ├── new_customer.py
│   ├── help.py
│   └── ...
└── users.db             # SQLite database (will be created automatically)
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram Bot Token from @BotFather | Yes |
| `ADMIN_SECRET_KEY` | Secret key for admin sessions | Yes |
| `PORT` | Port number (set by Railway) | Auto |

## Admin Panel Features

- 📊 Dashboard with order statistics
- 👥 User management
- 💳 Payment history
- 🛒 Order management
- 🔄 Cancel orders and refund tokens
- 📱 Send notifications to users

## Security Notes

1. **Generate Strong Secret Keys**: 
   - Use the provided `generate_secret.py` script
   - Never use default or weak keys
   
2. **Change Default Admin Credentials**: 
   - Edit `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `flaskapp/admin_app.py`
   
3. **Use Strong Secret Key**:
   - Generate a secure `ADMIN_SECRET_KEY` using the script
   - Use different keys for different environments
   
4. **Database Security**:
   - The SQLite database is stored in Railway's ephemeral filesystem
   - For production, consider using a persistent database

## Troubleshooting

### Bot Not Responding
- Check if `BOT_TOKEN` is correct
- Verify the bot is running in Railway logs
- Ensure webhook URL is correct (if using webhooks)

### Admin Panel Not Loading
- Check if `ADMIN_SECRET_KEY` is set
- Verify the URL: `https://your-app.railway.app/admin`
- Check Railway logs for errors

### Database Issues
- The database is created automatically on first run
- Check Railway logs for database errors
- Ensure proper file permissions

## Support

For issues and questions:
1. Check Railway logs
2. Verify environment variables
3. Test locally first
4. Check Telegram Bot API status

## License

This project is for educational purposes. Use responsibly. 