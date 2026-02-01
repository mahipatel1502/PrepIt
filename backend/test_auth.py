"""
Test script for authentication endpoints
Run this after starting the server to test the auth flow
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_signup():
    """Test user signup"""
    print("\n📝 Testing Signup...")
    
    data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "TestPass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=data)
    
    if response.status_code == 201:
        print("✅ Signup successful!")
        result = response.json()
        print(f"   User ID: {result['user']['user_id']}")
        print(f"   Name: {result['user']['full_name']}")
        print(f"   Email: {result['user']['email']}")
        return result['access_token']
    else:
        print(f"❌ Signup failed: {response.json()}")
        return None

def test_login(email, password):
    """Test user login"""
    print("\n🔐 Testing Login...")
    
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    
    if response.status_code == 200:
        print("✅ Login successful!")
        result = response.json()
        print(f"   Token: {result['access_token'][:50]}...")
        return result['access_token']
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def test_get_user_info(token):
    """Test getting current user info"""
    print("\n👤 Testing Get User Info...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        print("✅ User info retrieved!")
        user = response.json()
        print(f"   ID: {user['user_id']}")
        print(f"   Name: {user['full_name']}")
        print(f"   Email: {user['email']}")
        print(f"   Created: {user['created_at']}")
        return True
    else:
        print(f"❌ Failed to get user info: {response.json()}")
        return False

def test_update_user(token):
    """Test updating user information"""
    print("\n✏️  Testing Update User Info...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "full_name": "Updated Test User"
    }
    
    response = requests.put(f"{BASE_URL}/auth/me", json=data, headers=headers)
    
    if response.status_code == 200:
        print("✅ User info updated!")
        user = response.json()
        print(f"   New Name: {user['full_name']}")
        return True
    else:
        print(f"❌ Failed to update user info: {response.json()}")
        return False

def test_change_password(token):
    """Test changing password"""
    print("\n🔑 Testing Change Password...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "old_password": "TestPass123",
        "new_password": "NewTestPass456"
    }
    
    response = requests.post(f"{BASE_URL}/auth/change-password", json=data, headers=headers)
    
    if response.status_code == 200:
        print("✅ Password changed successfully!")
        return True
    else:
        print(f"❌ Failed to change password: {response.json()}")
        return False

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    print("\n🔒 Testing Protected Endpoint (Upload)...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Create a simple CSV file in memory
    files = {
        'file': ('test.csv', 'col1,col2\n1,2\n3,4', 'text/csv')
    }
    
    response = requests.post(f"{BASE_URL}/dataset/upload", files=files, headers=headers)
    
    if response.status_code == 200:
        print("✅ Protected endpoint accessed successfully!")
        return True
    else:
        print(f"❌ Failed to access protected endpoint: {response.json()}")
        return False

def test_invalid_token():
    """Test with invalid token"""
    print("\n🚫 Testing Invalid Token...")
    
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 401:
        print("✅ Invalid token correctly rejected!")
        return True
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print("🧪 PrepIt Authentication Test Suite")
    print("=" * 60)
    print("\n⚠️  Make sure the server is running on http://localhost:8000")
    print("⚠️  This will create a test user in your database")
    
    input("\nPress Enter to continue...")
    
    # Test signup
    token = test_signup()
    
    if token:
        # Test login
        token = test_login("test@example.com", "TestPass123")
        
        if token:
            # Test getting user info
            test_get_user_info(token)
            
            # Test updating user
            test_update_user(token)
            
            # Test changing password
            if test_change_password(token):
                # Login with new password
                token = test_login("test@example.com", "NewTestPass456")
            
            # Test protected endpoint
            if token:
                test_protected_endpoint(token)
            
            # Test invalid token
            test_invalid_token()
    
    print("\n" + "=" * 60)
    print("🏁 Test Suite Complete!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("   Please make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
