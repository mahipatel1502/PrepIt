import API_CONFIG from './api-config'

// Types
export interface User {
  user_id: string
  full_name: string
  email: string
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface SignupData {
  full_name: string
  email: string
  password: string
}

export interface LoginData {
  email: string
  password: string
}

export interface GoogleLoginData {
  id_token: string
}

export interface UpdateUserData {
  full_name?: string
  email?: string
}

export interface ChangePasswordData {
  old_password: string
  new_password: string
}

export interface ApiError {
  detail: string | { loc: string[]; msg: string; type: string }[]
}

// Token management
export const getToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(API_CONFIG.TOKEN_KEY)
}

export const setToken = (token: string): void => {
  if (typeof window === 'undefined') return
  localStorage.setItem(API_CONFIG.TOKEN_KEY, token)
}

export const removeToken = (): void => {
  if (typeof window === 'undefined') return
  localStorage.removeItem(API_CONFIG.TOKEN_KEY)
}

// API Client
class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = getToken()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    // Merge with provided headers
    if (options.headers) {
      Object.assign(headers, options.headers)
    }

    if (token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const url = `${this.baseUrl}${endpoint}`

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      const data = await response.json()

      if (!response.ok) {
        throw {
          status: response.status,
          message: this.extractErrorMessage(data),
          data,
        }
      }

      return data
    } catch (error: any) {
      if (error.status) {
        throw error
      }
      throw {
        status: 0,
        message: 'Network error. Please check your connection.',
        data: null,
      }
    }
  }

  private extractErrorMessage(errorData: ApiError): string {
    if (typeof errorData.detail === 'string') {
      return errorData.detail
    }
    if (Array.isArray(errorData.detail) && errorData.detail.length > 0) {
      return errorData.detail[0].msg
    }
    return 'An error occurred. Please try again.'
  }

  // Auth endpoints
  async signup(data: SignupData): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>(
      API_CONFIG.ENDPOINTS.AUTH.SIGNUP,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    )
    setToken(response.access_token)
    return response
  }

  async login(data: LoginData): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>(
      API_CONFIG.ENDPOINTS.AUTH.LOGIN,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    )
    setToken(response.access_token)
    return response
  }

  async loginWithGoogle(data: GoogleLoginData): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>(
      API_CONFIG.ENDPOINTS.AUTH.GOOGLE_LOGIN,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    )
    setToken(response.access_token)
    return response
  }

  async logout(): Promise<{ message: string }> {
    try {
      const response = await this.request<{ message: string }>(
        API_CONFIG.ENDPOINTS.AUTH.LOGOUT,
        {
          method: 'POST',
        }
      )
      removeToken()
      return response
    } catch (error) {
      // Even if API call fails, remove token locally
      removeToken()
      throw error
    }
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>(API_CONFIG.ENDPOINTS.AUTH.ME, {
      method: 'GET',
    })
  }

  async updateUser(data: UpdateUserData): Promise<User> {
    return this.request<User>(API_CONFIG.ENDPOINTS.AUTH.UPDATE, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async changePassword(data: ChangePasswordData): Promise<{ message: string }> {
    return this.request<{ message: string }>(
      API_CONFIG.ENDPOINTS.AUTH.CHANGE_PASSWORD,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    )
  }

  // Dataset endpoints
  async uploadDataset(file: File): Promise<any> {
    const token = getToken()
    const formData = new FormData()
    formData.append('file', file)

    const url = `${this.baseUrl}${API_CONFIG.ENDPOINTS.DATASET.UPLOAD}`

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    })

    const data = await response.json()

    if (!response.ok) {
      throw {
        status: response.status,
        message: this.extractErrorMessage(data),
        data,
      }
    }

    return data
  }
}

// Export singleton instance
export const apiClient = new ApiClient(API_CONFIG.BASE_URL)

export default apiClient
