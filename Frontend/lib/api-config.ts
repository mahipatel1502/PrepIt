// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
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
  },
  TOKEN_KEY: 'prepit_auth_token',
} as const

export default API_CONFIG
