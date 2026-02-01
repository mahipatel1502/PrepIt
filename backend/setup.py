"""
Quick setup script to generate .env file
"""

import secrets

print("=" * 60)
print("🚀 PrepIt Backend Setup")
print("=" * 60)

print("\n📝 Generating secure SECRET_KEY...")
secret_key = secrets.token_urlsafe(32)

print("\n✅ Generated SECRET_KEY:")
print(f"   {secret_key}\n")

env_content = f"""# JWT Configuration
SECRET_KEY={secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Firebase Configuration
# FIREBASE_CREDENTIALS_PATH=path/to/your/firebase-service-account.json

# Environment
ENVIRONMENT=development
"""

print("📄 Creating .env file...")
with open('.env', 'w') as f:
    f.write(env_content)

print("✅ .env file created successfully!\n")

print("=" * 60)
print("🎯 Next Steps:")
print("=" * 60)
print("1. ✅ Dependencies: pip install -r requirements.txt")
print("2. 🔥 Firebase: Add your Firebase credentials path to .env")
print("3. 🚀 Run Server: uvicorn app.main:app --reload")
print("4. 🧪 Test: python test_auth.py")
print("5. 📖 Docs: http://localhost:8000/docs")
print("\n📚 For detailed setup, see AUTH_SETUP.md")
print("=" * 60)
