"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { apiClient, getToken, removeToken, setToken } from "@/lib/api-client"
import type { User as ApiUser } from "@/lib/api-client"
import { signInWithGoogle, checkRedirectResult, onAuthChange, firebaseSignOut } from "@/lib/firebase"

interface User {
  id: string
  email: string
  name: string
  avatar?: string
  provider: "email" | "google"
  createdAt?: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  loginWithGoogle: () => Promise<void>
  signup: (email: string, password: string, name: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Transform API user to local user format
function transformUser(apiUser: ApiUser): User {
  return {
    id: apiUser.user_id,
    email: apiUser.email,
    name: apiUser.full_name,
    provider: "email",
    createdAt: apiUser.created_at,
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Check for existing session and Firebase redirect result on mount
  useEffect(() => {
    const initAuth = async () => {
      console.log("🔍 Checking auth state...")
      
      // First check for redirect result from Google sign-in
      try {
        const redirectResult = await checkRedirectResult()
        console.log("🔍 Redirect result:", redirectResult ? "User found" : "No redirect")
        
        if (redirectResult?.user) {
          // User signed in with Google via redirect
          const firebaseUser = redirectResult.user
          const idToken = await firebaseUser.getIdToken()
          
          console.log("✅ Google sign-in successful:", firebaseUser.email)
          
          // Store the Firebase token as our auth token
          setToken(idToken)
          
          // Set user from Firebase data
          const newUser = {
            id: firebaseUser.uid,
            email: firebaseUser.email || "",
            name: firebaseUser.displayName || firebaseUser.email?.split("@")[0] || "User",
            avatar: firebaseUser.photoURL || undefined,
            provider: "google" as const,
            createdAt: firebaseUser.metadata.creationTime,
          }
          
          setUser(newUser)
          setIsLoading(false)
          console.log("✅ User state set, isLoading set to false")
          return
        }
      } catch (error) {
        console.error("❌ Error checking redirect result:", error)
      }

      // Then check for existing backend session
      const token = getToken()
      if (token) {
        console.log("🔍 Found existing token, fetching user...")
        try {
          const userData = await apiClient.getCurrentUser()
          setUser(transformUser(userData))
          console.log("✅ User loaded from backend:", userData.email)
        } catch (error) {
          console.error("❌ Failed to fetch user:", error)
          removeToken()
        }
      }
      setIsLoading(false)
      console.log("✅ Auth initialization complete")
    }

    initAuth()

    // Listen to Firebase auth state changes
    const unsubscribe = onAuthChange(async (firebaseUser) => {
      console.log("🔍 Auth state changed:", firebaseUser ? firebaseUser.email : "No user")
      
      if (firebaseUser) {
        // User is signed in with Firebase
        const idToken = await firebaseUser.getIdToken()
        setToken(idToken)
        
        const newUser = {
          id: firebaseUser.uid,
          email: firebaseUser.email || "",
          name: firebaseUser.displayName || firebaseUser.email?.split("@")[0] || "User",
          avatar: firebaseUser.photoURL || undefined,
          provider: "google" as const,
          createdAt: firebaseUser.metadata.creationTime,
        }
        
        setUser(newUser)
        console.log("✅ User state updated from auth change:", newUser.email)
      }
    })

    return () => unsubscribe()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.login({ email, password })
      setUser(transformUser(response.user))
    } catch (error: any) {
      console.error("Login error:", error)
      throw new Error(error.message || "Invalid credentials. Please try again.")
    }
  }

  const loginWithGoogle = async () => {
    try {
      console.log("🔍 Starting Google login...")
      
      // Sign in with Firebase Google provider (popup first, redirect fallback)
      const result = await signInWithGoogle()
      
      console.log("✅ Google sign-in completed:", result.user.email)
      
      // Get the Firebase ID token
      const idToken = await result.user.getIdToken()
      
      // Store the Firebase token as our auth token
      setToken(idToken)
      
      // Set user from Firebase data
      const newUser = {
        id: result.user.uid,
        email: result.user.email || "",
        name: result.user.displayName || result.user.email?.split("@")[0] || "User",
        avatar: result.user.photoURL || undefined,
        provider: "google" as const,
        createdAt: result.user.metadata.creationTime,
      }
      
      setUser(newUser)
      console.log("✅ User state set in context:", newUser.email)
      
    } catch (error: any) {
      console.error("❌ Google login error:", error)
      
      // If it's the redirecting message, don't show error
      if (error.message?.includes("Redirecting")) {
        console.log("🔄 Redirecting to Google, auth will complete after redirect...")
        return
      }
      
      throw new Error(error.message || "Google sign-in failed. Please try again.")
    }
  }

  const signup = async (email: string, password: string, name: string) => {
    try {
      const response = await apiClient.signup({
        full_name: name,
        email,
        password,
      })
      setUser(transformUser(response.user))
    } catch (error: any) {
      console.error("Signup error:", error)
      throw new Error(error.message || "Signup failed. Please try again.")
    }
  }

  const logout = async () => {
    try {
      // Sign out from Firebase if logged in with Google
      await firebaseSignOut()
      
      // Also try to logout from backend if using email/password
      if (user?.provider === "email") {
        await apiClient.logout()
      }
    } catch (error) {
      console.error("Logout error:", error)
    } finally {
      setUser(null)
      removeToken()
    }
  }

  const refreshUser = async () => {
    try {
      const userData = await apiClient.getCurrentUser()
      setUser(transformUser(userData))
    } catch (error) {
      console.error("Failed to refresh user:", error)
      setUser(null)
      removeToken()
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        loginWithGoogle,
        signup,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
