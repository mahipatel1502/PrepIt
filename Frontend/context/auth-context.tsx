"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { apiClient, getToken, removeToken } from "@/lib/api-client"
import type { User as ApiUser } from "@/lib/api-client"

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

  // Check for existing session on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = getToken()
      if (token) {
        try {
          const userData = await apiClient.getCurrentUser()
          setUser(transformUser(userData))
        } catch (error) {
          console.error("Failed to fetch user:", error)
          removeToken()
        }
      }
      setIsLoading(false)
    }

    initAuth()
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
    // TODO: Implement Google OAuth when backend supports it
    throw new Error("Google login is not yet implemented. Please use email/password.")
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
      await apiClient.logout()
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
