/**
 * Token Management Utility
 * 
 * Clear invalid or expired tokens from localStorage
 * Use this if you're getting 401 Unauthorized errors after authentication changes
 */

export function clearAuthToken(): void {
  if (typeof window === 'undefined') return
  
  const tokenKey = 'prepit_auth_token'
  const oldToken = localStorage.getItem(tokenKey)
  
  if (oldToken) {
    console.log('🗑️ Clearing old authentication token...')
    localStorage.removeItem(tokenKey)
    console.log('✅ Token cleared successfully')
  } else {
    console.log('ℹ️ No token found to clear')
  }
}

/**
 * Check if current token is a Firebase ID token (starts with 'eyJ')
 * Old JWT tokens had different structure
 */
export function isValidFirebaseToken(token: string): boolean {
  if (!token || token.length < 10) return false
  
  try {
    // Firebase ID tokens are JWTs starting with 'eyJ'
    if (!token.startsWith('eyJ')) return false
    
    // Try to decode the header
    const parts = token.split('.')
    if (parts.length !== 3) return false
    
    const header = JSON.parse(atob(parts[0]))
    
    // Firebase tokens should have 'RS256' algorithm
    return header.alg === 'RS256'
  } catch {
    return false
  }
}

/**
 * Check and clean invalid tokens on app startup
 */
export function validateAndCleanToken(): void {
  if (typeof window === 'undefined') return
  
  const token = localStorage.getItem('prepit_auth_token')
  
  if (token && !isValidFirebaseToken(token)) {
    console.warn('⚠️ Invalid token format detected - clearing...')
    clearAuthToken()
  }
}

// Auto-run on import in development
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  // Check token validity on load
  const token = localStorage.getItem('prepit_auth_token')
  if (token) {
    const isValid = isValidFirebaseToken(token)
    console.log(`🔐 Token validation: ${isValid ? '✅ Valid Firebase token' : '❌ Invalid token format'}`)
    
    if (!isValid) {
      console.log('💡 Run clearAuthToken() in console to clear invalid token')
    }
  }
}

// Export for console access
if (typeof window !== 'undefined') {
  ;(window as any).clearAuthToken = clearAuthToken
  ;(window as any).validateAndCleanToken = validateAndCleanToken
}
