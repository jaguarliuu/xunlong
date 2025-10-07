import axios from 'axios'

// API基础URL - 开发环境使用本地，生产环境使用环境变量
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60秒超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

/**
 * API服务
 */
export const api = {
  // ========== 报告生成 ==========

  /**
   * 创建报告生成任务
   */
  createReport(data) {
    return apiClient.post('/api/v1/tasks/report', data)
  },

  // ========== 小说创作 ==========

  /**
   * 创建小说创作任务
   */
  createFiction(data) {
    return apiClient.post('/api/v1/tasks/fiction', data)
  },

  // ========== PPT生成 ==========

  /**
   * 创建PPT生成任务
   */
  createPPT(data) {
    return apiClient.post('/api/v1/tasks/ppt', data)
  },

  // ========== 任务管理 ==========

  /**
   * 获取任务状态
   */
  getTaskStatus(taskId) {
    return apiClient.get(`/api/v1/tasks/${taskId}`)
  },

  /**
   * 获取任务结果
   */
  getTaskResult(taskId) {
    return apiClient.get(`/api/v1/tasks/${taskId}/result`)
  },

  /**
   * 下载任务文件
   */
  downloadTaskFile(taskId, fileType = 'html') {
    const url = `${API_BASE_URL}/api/v1/tasks/${taskId}/download?file_type=${fileType}`
    window.open(url, '_blank')
  },

  /**
   * 取消任务
   */
  cancelTask(taskId) {
    return apiClient.delete(`/api/v1/tasks/${taskId}`)
  },

  /**
   * 列出所有任务
   */
  listTasks(params = {}) {
    return apiClient.get('/api/v1/tasks', { params })
  },

  // ========== 系统 ==========

  /**
   * 健康检查
   */
  healthCheck() {
    return apiClient.get('/health')
  }
}

export default api
