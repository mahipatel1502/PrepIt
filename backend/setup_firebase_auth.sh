#!/bin/bash
# Firebase Authentication Setup Script

echo "🔥 Firebase Authentication Setup"
echo "================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
fi

# Check for Firebase Web API Key
if grep -q "YOUR_WEB_API_KEY_HERE" .env || ! grep -q "FIREBASE_WEB_API_KEY" .env; then
    echo ""
    echo "⚠️  FIREBASE_WEB_API_KEY not configured!"
    echo ""
    echo "📝 To get your Firebase Web API Key:"
    echo "   1. Go to https://console.firebase.google.com"
    echo "   2. Select your project"
    echo "   3. Click the gear icon (⚙️) → Project Settings"
    echo "   4. Under 'General' tab, find 'Web API Key'"
    echo "   5. Copy the key (starts with 'AIza...')"
    echo ""
    read -p "Enter your Firebase Web API Key: " api_key
    
    if [[ ! -z "$api_key" ]]; then
        # Update .env file
        if grep -q "FIREBASE_WEB_API_KEY" .env; then
            sed -i "s/FIREBASE_WEB_API_KEY=.*/FIREBASE_WEB_API_KEY=$api_key/" .env
        else
            echo "FIREBASE_WEB_API_KEY=$api_key" >> .env
        fi
        echo "✅ API Key saved to .env"
    else
        echo "⚠️  No API key provided. Please update .env manually."
    fi
fi

echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Enable Email/Password in Firebase Console"
echo "   2. Run: uvicorn app.main:app --reload"
echo "   3. Test at http://localhost:8000/docs"
echo ""
echo "📚 Documentation:"
echo "   - MIGRATION_COMPLETE.md - Overview and next steps"
echo "   - FIREBASE_AUTH_MIGRATION.md - Detailed migration guide"
echo "   - FIREBASE_AUTH_QUICKREF.md - API quick reference"
