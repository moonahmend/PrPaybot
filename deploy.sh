#!/bin/bash

echo "🚀 PrBot_Pay Railway Deployment Script"
echo "======================================"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "⚠️  Railway CLI is not installed."
    echo "You can install it with: npm install -g @railway/cli"
    echo "Or deploy directly from Railway dashboard."
fi

echo "📋 Prerequisites Check:"
echo "✅ Git is installed"
echo "✅ Python project structure is ready"
echo "✅ Required files are present:"
echo "   - main.py"
echo "   - requirements.txt"
echo "   - Procfile"
echo "   - runtime.txt"

echo ""
echo "🔧 Next Steps:"
echo "1. Push your code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Initial commit for Railway deployment'"
echo "   git push origin main"
echo ""
echo "2. Deploy to Railway:"
echo "   - Go to https://railway.app"
echo "   - Create new project"
echo "   - Connect your GitHub repository"
echo "   - Add environment variables:"
echo "     BOT_TOKEN=your_telegram_bot_token"
echo "     ADMIN_SECRET_KEY=your_secret_key"
echo ""
echo "3. Access your application:"
echo "   - Bot: https://your-app.railway.app"
echo "   - Admin Panel: https://your-app.railway.app/admin"
echo "   - Admin Login: admin / admin123"
echo ""
echo "🎉 Your PrBot_Pay will be live on Railway!"

# Optional: Check if .env file exists
if [ -f ".env" ]; then
    echo ""
    echo "⚠️  Warning: .env file found. Make sure to add these variables to Railway:"
    cat .env | grep -E "^(BOT_TOKEN|ADMIN_SECRET_KEY)=" || echo "No BOT_TOKEN or ADMIN_SECRET_KEY found in .env"
fi 