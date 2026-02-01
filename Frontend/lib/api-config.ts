// API Configuration
// Validate API URL in production
const getApiUrl = () => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://prepit-copy.onrender.com'
  
  // Log warning in production if using localhost
  if (process.env.NODE_ENV === 'production' && apiUrl.includes('localhost')) {
    console.warn('⚠️ Warning: Using localhost API URL in production. Please set NEXT_PUBLIC_API_URL environment variable.')
  }
  
  return apiUrl
}

export const API_CONFIG = {
  BASE_URL: getApiUrl(),
  ENDPOINTS: {
    AUTH: {
      SIGNUP: '/api/auth/signup',
      LOGIN: '/api/auth/login',
      GOOGLE_LOGIN: '/api/auth/google',
      LOGOUT: '/api/auth/logout',
      ME: '/api/auth/me',
      UPDATE: '/api/auth/me',
      CHANGE_PASSWORD: '/api/auth/change-password',
    },
    DATASET: {
      UPLOAD: '/api/dataset/upload',
    },
    HISTORY: {
      LIST: '/api/history',
      DETAIL: (historyId: string) => `/api/history/${historyId}`,
      DELETE: (historyId: string) => `/api/history/${historyId}`,
      STATS: '/api/history/stats/summary',
    },
  },
  TOKEN_KEY: 'prepit_auth_token',
} as const

export default API_CONFIG
