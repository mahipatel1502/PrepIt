from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from google.api_core import exceptions as google_exceptions
from google.cloud.firestore_v1.base_query import FieldFilter
from app.models.user import (
    UserSignup, 
    UserLogin, 
    TokenResponse, 
    UserResponse, 
    MessageResponse,
    UserUpdate,
    PasswordChange
)
from app.utils.firebase_config import get_db
from app.utils.jwt_handler import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.utils.auth_middleware import get_current_user

router = APIRouter()

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup):
    """
    Create a new user account
    
    - **full_name**: User's full name (2-100 characters)
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars, 1 uppercase, 1 digit)
    """
    try:
        db = get_db()
        
        # Check if user already exists
        users_ref = db.collection('users')
        existing_user = users_ref.where(filter=FieldFilter('email', '==', user_data.email)).limit(1).get()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user document
        user_doc = {
            'full_name': user_data.full_name,
            'email': user_data.email,
            'password_hash': hashed_password,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Save to Firestore
        doc_ref = users_ref.document()
        doc_ref.set(user_doc)
        user_id = doc_ref.id
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user_id,
                "email": user_data.email,
                "full_name": user_data.full_name
            },
            expires_delta=access_token_expires
        )
        
        # Return token and user info
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                user_id=user_id,
                full_name=user_data.full_name,
                email=user_data.email,
                created_at=user_doc['created_at']
            )
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except google_exceptions.NotFound:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured. Please contact administrator to set up Firestore database."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login with email and password
    
    - **email**: Registered email address
    - **password**: User password
    """
    try:
        db = get_db()
        
        # Find user by email
        users_ref = db.collection('users')
        user_docs = users_ref.where(filter=FieldFilter('email', '==', credentials.email)).limit(1).get()
        
        if not user_docs:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        user_doc = user_docs[0]
        user_data = user_doc.to_dict()
        user_id = user_doc.id
        
        # Verify password
        if not verify_password(credentials.password, user_data['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user_id,
                "email": user_data['email'],
                "full_name": user_data['full_name']
            },
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                user_id=user_id,
                full_name=user_data['full_name'],
                email=user_data['email'],
                created_at=user_data['created_at']
            )
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except google_exceptions.NotFound:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured. Please contact administrator to set up Firestore database."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Requires: Bearer token in Authorization header
    """
    db = get_db()
    
    user_doc = db.collection('users').document(current_user['user_id']).get()
    
    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_data = user_doc.to_dict()
    
    return UserResponse(
        user_id=user_doc.id,
        full_name=user_data['full_name'],
        email=user_data['email'],
        created_at=user_data['created_at']
    )

@router.put("/me", response_model=UserResponse)
async def update_user_info(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user information
    
    Requires: Bearer token in Authorization header
    """
    db = get_db()
    user_ref = db.collection('users').document(current_user['user_id'])
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prepare update data
    update_data = {}
    if user_update.full_name is not None:
        update_data['full_name'] = user_update.full_name
    if user_update.email is not None:
        # Check if new email is already taken
        users_ref = db.collection('users')
        existing = users_ref.where(filter=FieldFilter('email', '==', user_update.email)).limit(1).get()
        if existing and existing[0].id != current_user['user_id']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        update_data['email'] = user_update.email
    
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    # Update user document
    user_ref.update(update_data)
    
    # Get updated user data
    updated_doc = user_ref.get()
    updated_data = updated_doc.to_dict()
    
    return UserResponse(
        user_id=updated_doc.id,
        full_name=updated_data['full_name'],
        email=updated_data['email'],
        created_at=updated_data['created_at']
    )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password
    
    Requires: Bearer token in Authorization header
    """
    db = get_db()
    user_ref = db.collection('users').document(current_user['user_id'])
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_data = user_doc.to_dict()
    
    # Verify old password
    if not verify_password(password_data.old_password, user_data['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Hash new password
    new_hashed_password = get_password_hash(password_data.new_password)
    
    # Update password
    user_ref.update({
        'password_hash': new_hashed_password,
        'updated_at': datetime.utcnow().isoformat()
    })
    
    return MessageResponse(message="Password changed successfully")

@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user (client should discard the token)
    
    Requires: Bearer token in Authorization header
    """
    # In a stateless JWT system, logout is handled client-side by discarding the token
    # If you need server-side token invalidation, implement a token blacklist
    return MessageResponse(message="Logged out successfully")
