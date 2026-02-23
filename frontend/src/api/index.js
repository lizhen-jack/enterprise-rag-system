import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE = '/api/v1'

export const request = axios.create({
  baseURL: API_BASE,
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessage.error('未授权，请重新登录')
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(error.response.data?.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

// 用户API
export const login = (formData) => {
  return axios.post('/users/login', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getUserInfo = () => request.get('/users/me')

// 文档API
export const uploadDocument = (file, title, description) => {
  const formData = new FormData()
  formData.append('file', file)
  if (title) formData.append('title', title)
  if (description) formData.append('description', description)

  return axios.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getDocuments = (params) => request.get('/documents', { params })
export const getDocumentDetail = (id) => request.get(`/documents/${id}`)
export const deleteDocument = (id) => request.delete(`/documents/${id}`)

// 对话API
export const chat = (data) => request.post('/chat/chat', data)
export const getConversations = (params) => request.get('/chat/conversations', { params })
export const getMessages = (conversationId, params) => request.get(`/chat/conversations/${conversationId}/messages`, { params })

// 记忆API
export const addMemory = (data) => request.post('/memory', data)
export const getMemories = (params) => request.get('/memory', { params })
export const retrieveMemories = (data) => request.post('/memory/retrieve', data)
export const deleteMemory = (id) => request.delete(`/memory/${id}`)
