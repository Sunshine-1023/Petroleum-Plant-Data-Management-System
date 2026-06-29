import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      error.userMessage = '网络异常或后端服务不可用'
    } else if (error.response.status >= 500) {
      error.userMessage = '服务器内部错误，请稍后重试'
    } else {
      error.userMessage = error.response?.data?.message || '请求失败'
    }
    return Promise.reject(error)
  },
)

export const loginByDbUser = (username, password) =>
  api.post('/auth/login/', { username, password })

export const getSystemStatus = () => api.get('/system/status/')
export const getStats = () => api.get('/stats/')
export const getDbTest = () => api.get('/db-test/')
export const getDepts = () => api.get('/depts/')
export const getDeptOverview = (deptCode) => api.get(`/depts/${deptCode}/overview/`)
export const getProjectDetail = (billNo) => api.get(`/projects/${billNo}/`)
export const updateProjectCosts = (billNo, data) => api.put(`/projects/${billNo}/costs/`, data)
export const getProjectMaterialView = () => api.get('/views/project-material/')
export const getDeptCostProcedure = (deptCode) => api.get(`/procedures/dept-cost/${deptCode}/`)
export const getCursorDeptSummary = () => api.get('/cursor/dept-summary/')
export const createProjectWithMaterials = (data) => api.post('/projects/create-with-materials/', data)

export default api
