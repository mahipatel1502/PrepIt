import { initializeApp, getApps, type FirebaseApp } from "firebase/app"
import { 
  getAuth, 
  GoogleAuthProvider, 
  signInWithPopup,
  signInWithRedirect,
  getRedirectResult,
  onAuthStateChanged,
  type Auth, 
  type UserCredential,
  type User as FirebaseUser
} from "firebase/auth"

// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
}

// Initialize Firebase (only if it hasn't been initialized yet)
let app: FirebaseApp
let auth: Auth
let googleProvider: GoogleAuthProvider

if (typeof window !== "undefined") {
  // Only initialize on client side
  if (!getApps().length) {
    app = initializeApp(firebaseConfig)
  } else {
    app = getApps()[0]
  }
  
  auth = getAuth(app)
  googleProvider = new GoogleAuthProvider()
  
  // Optional: Add custom parameters
  googleProvider.setCustomParameters({
    prompt: "select_account"
  })
}

/**
 * Sign in with Google using Firebase popup (with fallback to redirect)
 * @returns Promise that resolves with UserCredential
 */
export async function signInWithGoogle(): Promise<UserCredential> {
  if (typeof window === "undefined") {
    throw new Error("signInWithGoogle can only be called on the client side")
  }
  
  try {
    console.log("🔍 Attempting Google sign-in with popup...")
    const result = await signInWithPopup(auth, googleProvider)
    console.log("✅ Popup sign-in successful:", result.user.email)
    return result
  } catch (error: any) {
    console.error("❌ Popup sign-in error:", error.code, error.message)
    
    // If popup fails due to COOP or popup blocked, try redirect
    if (
      error.code === "auth/popup-blocked" || 
      error.code === "auth/popup-closed-by-user" ||
      error.message?.includes("Cross-Origin-Opener-Policy")
    ) {
      console.log("🔄 Falling back to redirect method...")
      await signInWithRedirect(auth, googleProvider)
      // This will never return as page will redirect
      throw new Error("Redirecting to Google sign-in...")
    }
    
    throw new Error(error.message || "Failed to sign in with Google. Please try again.")
  }
}

/**
 * Check for redirect result after Google sign-in
 * Call this on app initialization
 * @returns UserCredential if redirect was successful, null otherwise
 */
export async function checkRedirectResult(): Promise<UserCredential | null> {
  if (typeof window === "undefined") {
    return null
  }
  
  try {
    const result = await getRedirectResult(auth)
    return result
  } catch (error: any) {
    console.error("Error getting redirect result:", error)
    
    // Handle specific error codes
    if (error.code === "auth/popup-closed-by-user") {
      throw new Error("Sign-in cancelled. Please try again.")
    } else if (error.code === "auth/popup-blocked") {
      throw new Error("Pop-up blocked. Please allow pop-ups for this site.")
    } else if (error.code === "auth/cancelled-popup-request") {
      throw new Error("Another sign-in is in progress. Please wait.")
    } else {
      throw new Error(error.message || "Failed to sign in with Google. Please try again.")
    }
  }
}

/**
 * Subscribe to Firebase auth state changes
 * @param callback Function to call when auth state changes
 * @returns Unsubscribe function
 */
export function onAuthChange(callback: (user: FirebaseUser | null) => void) {
  if (typeof window === "undefined") {
    return () => {}
  }
  return onAuthStateChanged(auth, callback)
}

/**
 * Get the current Firebase ID token for the authenticated user
 * @returns ID token string or null if no user is signed in
 */
export async function getFirebaseIdToken(): Promise<string | null> {
  if (typeof window === "undefined" || !auth.currentUser) {
    return null
  }
  
  try {
    const token = await auth.currentUser.getIdToken()
    return token
  } catch (error) {
    console.error("Error getting Firebase ID token:", error)
    return null
  }
}

/**
 * Sign out from Firebase
 */
export async function firebaseSignOut(): Promise<void> {
  if (typeof window === "undefined") {
    return
  }
  
  try {
    await auth.signOut()
  } catch (error) {
    console.error("Error signing out from Firebase:", error)
  }
}

export { auth, googleProvider }
