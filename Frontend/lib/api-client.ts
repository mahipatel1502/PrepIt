import API_CONFIG from './api-config'

// Types
export interface User {
  user_id: string
  full_name: string
  email: string
  email_verified: boolean
}

export interface AuthResponse {
  id_token: string
  refresh_token: string
  expires_in: number
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

// Dataset & Preprocessing Types
export interface PreprocessingConfig {
  target_column?: string
  missing_threshold?: number
  outlier_method?: 'cap' | 'remove' | 'none'
  cardinality_threshold?: number
  scaling_method?: 'auto' | 'minmax' | 'standard' | 'robust'
}

export interface PreprocessingReport {
  original_shape?: [number, number]
  processed_shape?: [number, number]
  missing_values_handled?: number
  outliers_handled?: number
  columns_dropped?: string[]
  categorical_encoded?: string[]
  numerical_scaled?: string[]
  [key: string]: any
}

export interface UploadResponse {
  status: string
  original_file_url?: string
  processed_file_url?: string
  history_id?: string
  preprocessing_report?: PreprocessingReport
  message: string
  error_code?: string
}

// History Types
export interface FileInfo {
  file_name: string
  bucket_path: string
  file_url?: string
  download_url?: string
}

export interface HistorySummary {
  history_id: string
  original_file_name: string
  processed_file_name?: string | null
  file_type: string
  status: string
  created_at: string
}

export interface HistoryRecord {
  history_id: string
  user_id: string
  file_id: string
  original_file: FileInfo
  processed_file?: FileInfo | null
  file_type: string
  status: string
  created_at: string
  preprocessing_version: string
  preprocessing_report?: PreprocessingReport | null
}

export interface HistoryListResponse {
  status: string
  total_count: number
  returned_count: number
  data: HistorySummary[]
}

export interface HistoryDetailResponse {
  status: string
  data: HistoryRecord
}

export interface HistoryDeleteResponse {
  status: string
  message: string
  deleted_files?: string[] | null
}

export interface HistoryStats {
  status: string
  data: {
    total_records: number
    successful_processings: number
    failed_processings: number
    success_rate: number
    recent_activity: Array<{
      history_id: string
      file_name: string
      status: string
      created_at: string
    }>
  }
}

export interface HistoryInsightsData {
  history_id: string
  original_file_name: string
  processed_file_name?: string | null
  created_at: string
  status: string
  profile_version?: string
  profile_generated_at?: string
  profile_storage_mode?: "full" | "compact" | "minimal" | string
  summary: {
    original_rows: number
    processed_rows: number
    original_columns: number
    processed_columns: number
    rows_removed: number
    columns_added: number
    columns_dropped: number
    duplicates_removed: number
    features_engineered: number
    processing_time_seconds: number
    data_quality_score: number
  }
  column_type_distribution: Array<{
    name: string
    value: number
  }>
  dataset_overview?: {
    rows: number
    columns: number
    total_cells: number
    missing_cells: number
    completeness_pct: number
    duplicate_rows: number
  }
  column_details?: Array<{
    column: string
    type: string
    missing_count: number
    missing_pct: number
    unique_count: number
    sample_values?: string[]
  }>
  missing_values_by_column?: Array<{
    column: string
    missing_count: number
    missing_pct: number
  }>
  numerical_statistics?: Array<{
    column: string
    mean: number | null
    median: number | null
    std: number | null
    min: number | null
    max: number | null
    q1: number | null
    q3: number | null
    skewness: number | null
    count: number
    histogram?: Array<{
      start: number | null
      end: number | null
      count: number
    }>
  }>
  correlation_pairs?: Array<{
    left: string
    right: string
    pair: string
    correlation: number | null
    abs_correlation: number | null
  }>
  correlation_matrix?: {
    columns: string[]
    values: Array<Array<number | null>>
  }
  categorical_distributions?: Array<{
    column: string
    unique_count: number
    top_values: Array<{
      value: string
      count: number
      pct: number
    }>
  }>
  outlier_summary?: Array<{
    column: string
    outlier_count: number
    outlier_pct: number
  }>
  highlights?: string[]
  limits?: Record<string, number>
  truncated?: Record<string, boolean>
  dropped_columns: string[]
  removed_non_informative_columns: string[]
  final_columns_sample: string[]
  report_timestamp?: string
}

export interface HistoryInsightsResponse {
  status: string
  data: HistoryInsightsData
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
      const connectionHint = this.baseUrl.includes("localhost")
        ? `Cannot connect to API at ${this.baseUrl}. Make sure backend server is running.`
        : `Cannot connect to API at ${this.baseUrl}.`
      throw {
        status: 0,
        message: connectionHint,
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
    setToken(response.id_token)
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
    setToken(response.id_token)
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
    setToken(response.id_token)
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
  async uploadDataset(
    file: File,
    config?: PreprocessingConfig
  ): Promise<UploadResponse> {
    const token = getToken()
    const formData = new FormData()
    formData.append('file', file)

    // Add preprocessing config as form fields
    if (config) {
      if (config.target_column) {
        formData.append('target_column', config.target_column)
      }
      if (config.missing_threshold !== undefined) {
        formData.append('missing_threshold', config.missing_threshold.toString())
      }
      if (config.outlier_method) {
        formData.append('outlier_method', config.outlier_method)
      }
      if (config.cardinality_threshold !== undefined) {
        formData.append('cardinality_threshold', config.cardinality_threshold.toString())
      }
      if (config.scaling_method) {
        formData.append('scaling_method', config.scaling_method)
      }
    }

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

  // History endpoints
  async getHistory(
    limit: number = 50,
    offset: number = 0,
    includeTotal: boolean = true
  ): Promise<HistoryListResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
      include_total: includeTotal.toString(),
    })

    return this.request<HistoryListResponse>(
      `${API_CONFIG.ENDPOINTS.HISTORY.LIST}?${params}`,
      { method: 'GET' }
    )
  }

  async getCompletedFiles(
    limit: number = 50,
    offset: number = 0,
    includeTotal: boolean = false
  ): Promise<HistoryListResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
      include_total: includeTotal.toString(),
    })

    return this.request<HistoryListResponse>(
      `${API_CONFIG.ENDPOINTS.HISTORY.COMPLETED_FILES}?${params}`,
      { method: 'GET' }
    )
  }

  async getHistoryDetail(historyId: string): Promise<HistoryDetailResponse> {
    return this.request<HistoryDetailResponse>(
      API_CONFIG.ENDPOINTS.HISTORY.DETAIL(historyId),
      { method: 'GET' }
    )
  }

  async deleteHistory(
    historyId: string,
    deleteFiles: boolean = true
  ): Promise<HistoryDeleteResponse> {
    const params = new URLSearchParams({
      delete_files: deleteFiles.toString(),
    })

    return this.request<HistoryDeleteResponse>(
      `${API_CONFIG.ENDPOINTS.HISTORY.DELETE(historyId)}?${params}`,
      { method: 'DELETE' }
    )
  }

  async getHistoryStats(): Promise<HistoryStats> {
    return this.request<HistoryStats>(API_CONFIG.ENDPOINTS.HISTORY.STATS, {
      method: 'GET',
    })
  }

  async getHistoryInsights(historyId: string): Promise<HistoryInsightsResponse> {
    return this.request<HistoryInsightsResponse>(
      API_CONFIG.ENDPOINTS.HISTORY.INSIGHTS(historyId),
      { method: 'GET' }
    )
  }
}

// Export singleton instance
export const apiClient = new ApiClient(API_CONFIG.BASE_URL)

export default apiClient
