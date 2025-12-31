import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 图片相关
export const getImages = () => api.get('/images')
export const getImageUrl = (filename) => `/api/images/${encodeURIComponent(filename)}`
export const getLabeledImageUrl = (filename) => `/api/labeled-images/${encodeURIComponent(filename)}`

// 标注相关
export const getLabels = (page = 1, perPage = 50) =>
  api.get('/labels', { params: { page, per_page: perPage } })
export const getLabel = (id) => api.get(`/labels/${id}`)
export const createLabel = (data) => api.post('/labels', data)
export const updateLabel = (id, data) => api.put(`/labels/${id}`, data)
export const deleteLabel = (id) => api.delete(`/labels/${id}`)
export const exportLabels = () => window.open('/api/labels/export', '_blank')

// 航司相关
export const getAirlines = () => api.get('/airlines')
export const createAirline = (data) => api.post('/airlines', data)

// 机型相关
export const getAircraftTypes = () => api.get('/aircraft-types')
export const createAircraftType = (data) => api.post('/aircraft-types', data)

// 统计相关
export const getStats = () => api.get('/stats')

export default api
