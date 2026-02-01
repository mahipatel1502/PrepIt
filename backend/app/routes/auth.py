from fastapi import APIRouter, HTTPException, status, Depends
from firebase_admin import auth
from firebase_admin.auth import UserNotFoundError, EmailAlreadyExistsError
import requests
import os
from dotenv import load_dotenv
from app.models.user import (
    UserSignup, 
    UserLogin, 
    TokenResponse, 
    UserResponse, 
    MessageResponse,
    UserUpdate,
    PasswordChange
)
from app.utils.firebase_config import get_auth
from app.utils.auth_middleware import get_current_user

load_dotenv()

router = APIRouter()

# Firebase Web API Key - get from Firebase Console
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup):
    """
    Create a new user account with Firebase Authentication
    
    - **full_name**: User's full name (2-100 characters)
    - **email**: Valid email address
    - **password**: Password (min 6 characters - Firebase requirement)
    """
    try:
        auth_client = get_auth()
        
        # Create user in Firebase Authentication
        user_record = auth_client.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.full_name
        )
        
        # Sign in the user to get tokens using Firebase REST API
        signin_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        signin_data = {
            "email": user_data.email,
            "password": user_data.password,
            "returnSecureToken": True
        }
        
        response = requests.post(signin_url, json=signin_data)
        
        if response.status_code != 200:
            # If sign-in fails, delete the created user
            auth_client.delete_user(user_record.uid)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate authentication tokens"
            )
        
        tokens = response.json()
        
        return TokenResponse(
            id_token=tokens['idToken'],
            refresh_token=tokens['refreshToken'],
            expires_in=int(tokens['expiresIn']),
            user=UserResponse(
                user_id=user_record.uid,
                full_name=user_data.full_name,
                email=user_data.email,
                email_verified=False
            )
        )
    
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login with email and password using Firebase Authentication
    
    - **email**: Registered email address
    - **password**: User password
    """
    try:
        # Sign in using Firebase REST API
        signin_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        signin_data = {
            "email": credentials.email,
            "password": credentials.password,
            "returnSecureToken": True
        }
        
        response = requests.post(signin_url, json=signin_data)
        
        if response.status_code != 200:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'Login failed')
            
            if 'INVALID_PASSWORD' in error_message or 'EMAIL_NOT_FOUND' in error_message:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        tokens = response.json()
        
        # Get user info from Firebase Auth
        auth_client = get_auth()
        user_record = auth_client.get_user(tokens['localId'])
        
        return TokenResponse(
            id_token=tokens['idToken'],
            refresh_token=tokens['refreshToken'],
            expires_in=int(tokens['expiresIn']),
            user=UserResponse(
                user_id=user_record.uid,
                full_name=user_record.display_name or "",
                email=user_record.email,
                email_verified=user_record.email_verified
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Requires: Bearer token (Firebase ID token) in Authorization header
    """
    try:
        auth_client = get_auth()
        user_record = auth_client.get_user(current_user['user_id'])
        
        return UserResponse(
            user_id=user_record.uid,
            full_name=user_record.display_name or "",
            email=user_record.email,
            email_verified=user_record.email_verified
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )

@router.put("/me", response_model=UserResponse)
async def update_user_info(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user information
    
    Requires: Bearer token (Firebase ID token) in Authorization header
    """
    try:
        auth_client = get_auth()
        
        # Prepare update data
        update_data = {}
        if user_update.full_name is not None:
            update_data['display_name'] = user_update.full_name
        
        # Update user in Firebase Auth
        auth_client.update_user(current_user['user_id'], **update_data)
        
        # Get updated user data
        user_record = auth_client.get_user(current_user['user_id'])
        
        return UserResponse(
            user_id=user_record.uid,
            full_name=user_record.display_name or "",
            email=user_record.email,
            email_verified=user_record.email_verified
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Update failed: {str(e)}"
        )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password
    
    Requires: Bearer token (Firebase ID token) in Authorization header
    """
    try:
        auth_client = get_auth()
        
        # Update password in Firebase Auth
        auth_client.update_user(
            current_user['user_id'],
            password=password_data.new_password
        )
        
        return MessageResponse(message="Password changed successfully")
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}"
        )

@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user
    
    Requires: Bearer token (Firebase ID token) in Authorization header
    Note: Client should discard the token. For enhanced security, 
    you can revoke refresh tokens on the server side.
    """
    try:
        auth_client = get_auth()
        # Revoke all refresh tokens for the user
        auth_client.revoke_refresh_tokens(current_user['user_id'])
        
        return MessageResponse(message="Logged out successfully. All refresh tokens have been revoked.")
    except Exception as e:
        # Even if revocation fails, inform client to discard token
        return MessageResponse(message="Logged out successfully")

