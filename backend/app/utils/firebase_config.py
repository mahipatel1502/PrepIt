import firebase_admin
from firebase_admin import credentials, firestore
from google.api_core import exceptions as google_exceptions
import os
from dotenv import load_dotenv

load_dotenv()

db = None

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global db
    
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Initialize Firebase
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        
        if not cred_path:
            raise ValueError(
                "FIREBASE_CREDENTIALS_PATH environment variable is not set. "
                "Please configure it in your .env file."
            )
        
        if not os.path.exists(cred_path):
            raise FileNotFoundError(
                f"Firebase credentials file not found at: {cred_path}. "
                "Please ensure the firebase-credentials.json file exists."
            )
        
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            
            # Test database connection by checking if we can access it
            # This will fail early if the database doesn't exist
            db.collection('_health_check')
            
        except google_exceptions.NotFound as e:
            raise RuntimeError(
                "Firebase Firestore database does not exist. "
                "Please create a Firestore database in the Firebase Console: "
                "https://console.firebase.google.com -> Firestore Database -> Create database"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Firebase: {str(e)}. "
                "Please check your firebase-credentials.json file."
            ) from e
    
    return db

def get_db():
    """Get Firestore database instance"""
    global db
    if db is None:
        db = initialize_firebase()
    return db
