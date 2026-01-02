<template>
  <div class="label-list">
    <div class="list-header">
      <h3>已标注记录</h3>
      <div class="header-actions">
        <button @click="exportCsv" class="export-btn">
          导出 CSV
        </button>
        <button @click="exportYolo" class="export-btn yolo">
          导出 YOLO
        </button>
        <button @click="exportImagesBtn" class="export-btn images">
          导出照片
        </button>
        <button @click="loadLabels" class="refresh-btn">
          刷新
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else-if="labels.length === 0" class="empty">
      暂无标注记录
    </div>

    <div v-else>
      <table class="labels-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>文件名</th>
            <th>机型</th>
            <th>航司</th>
            <th>注册号</th>
            <th>清晰度</th>
            <th>遮挡度</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="label in labels" :key="label.id">
            <td class="id-col">{{ label.id }}</td>
            <td class="filename">{{ label.file_name }}</td>
            <td>{{ label.type_id }}</td>
            <td>{{ label.airline_id }}</td>
            <td>{{ label.registration }}</td>
            <td>{{ label.clarity.toFixed(2) }}</td>
            <td>{{ label.block.toFixed(2) }}</td>
            <td class="actions">
              <button @click="viewLabel(label)" class="view-btn">查看</button>
              <button @click="editLabel(label)" class="edit-btn">编辑</button>
              <button @click="confirmDelete(label)" class="delete-btn">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="pagination">
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage <= 1">
          上一页
        </button>
        <span class="page-info">
          第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
          ({{ total }} 条记录)
        </span>
        <button @click="goToPage(currentPage + 1)" :disabled="currentPage >= totalPages">
          下一页
        </button>
      </div>
    </div>

    <!-- 查看/编辑对话框 -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ modalMode === 'view' ? '查看标注' : '编辑标注' }}</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>

        <div class="modal-body">
          <!-- 图片预览（查看模式使用 BoundingBox 只读显示，编辑模式可修改） -->
          <div class="preview-section">
            <BoundingBox
              v-if="modalMode === 'view'"
              :imageSrc="getLabeledImageUrl(selectedLabel.file_name)"
              :imageWidth="imageSize.width"
              :imageHeight="imageSize.height"
              :initialRegistrationBox="parseYoloArea(selectedLabel.registration_area, imageSize.width, imageSize.height)"
              :readonly="true"
            />
            <BoundingBox
              v-else
              ref="boundingBoxRef"
              :imageSrc="getLabeledImageUrl(selectedLabel.file_name)"
              :imageWidth="imageSize.width"
              :imageHeight="imageSize.height"
              :initialRegistrationBox="editForm.registrationBox"
              @update:registrationBox="onBoxUpdate"
            />
          </div>

          <!-- 标注信息 -->
          <div class="label-info">
            <div class="info-row">
              <label>文件名</label>
              <span>{{ selectedLabel.file_name }}</span>
            </div>

            <div v-if="modalMode === 'view'">
              <div class="info-row">
                <label>机型</label>
                <span>{{ selectedLabel.type_id }} - {{ selectedLabel.type_name }}</span>
              </div>
              <div class="info-row">
                <label>航司</label>
                <span>{{ selectedLabel.airline_id }} - {{ selectedLabel.airline_name }}</span>
              </div>
              <div class="info-row">
                <label>注册号</label>
                <span>{{ selectedLabel.registration }}</span>
              </div>
              <div class="info-row">
                <label>清晰度</label>
                <span>{{ selectedLabel.clarity.toFixed(2) }}</span>
              </div>
              <div class="info-row">
                <label>遮挡度</label>
                <span>{{ selectedLabel.block.toFixed(2) }}</span>
              </div>
              <div class="info-row">
                <label>注册号区域</label>
                <span class="area">{{ selectedLabel.registration_area }}</span>
              </div>
            </div>

            <div v-else class="edit-form">
              <div class="info-row">
                <label>机型</label>
                <select v-model="editForm.typeId" @change="onTypeChange">
                  <option v-for="type in aircraftTypes" :key="type.code" :value="type.code">
                    {{ type.code }} - {{ type.name }}
                  </option>
                </select>
              </div>
              <div class="info-row">
                <label>航司</label>
                <select v-model="editForm.airlineId" @change="onAirlineChange">
                  <option v-for="airline in airlines" :key="airline.code" :value="airline.code">
                    {{ airline.code }} - {{ airline.name }}
                  </option>
                </select>
              </div>
              <div class="info-row">
                <label>注册号</label>
                <input v-model="editForm.registration" />
              </div>
              <div class="info-row">
                <label>清晰度: {{ editForm.clarity.toFixed(2) }}</label>
                <input type="range" v-model.number="editForm.clarity" min="0" max="1" step="0.01" />
              </div>
              <div class="info-row">
                <label>遮挡度: {{ editForm.block.toFixed(2) }}</label>
                <input type="range" v-model.number="editForm.block" min="0" max="1" step="0.01" />
              </div>
              <div class="info-row">
                <label>注册号区域</label>
                <span class="area">{{ editForm.registrationArea }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button v-if="modalMode === 'edit'" @click="saveEdit" class="save-btn" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
          <button @click="closeModal" class="cancel-btn">
            {{ modalMode === 'view' ? '关闭' : '取消' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal confirm-modal">
        <h3>确认删除</h3>
        <p>确定要删除标注 "{{ labelToDelete?.file_name }}" 吗？</p>
        <p class="warning">此操作不可撤销！</p>
        <div class="modal-footer">
          <button @click="doDelete" class="delete-btn" :disabled="deleting">
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
          <button @click="cancelDelete" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>

    <!-- 导出选项对话框 -->
    <div v-if="showExportModal" class="modal-overlay" @click.self="closeExportModal">
      <div class="modal export-modal">
        <div class="modal-header">
          <h3>导出选项</h3>
          <button @click="closeExportModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="export-options">
            <div class="option-group">
              <label class="radio-label">
                <input type="radio" v-model="exportRange" value="all" />
                导出全部 (共 {{ total }} 条记录)
              </label>
            </div>
            <div class="option-group">
              <label class="radio-label">
                <input type="radio" v-model="exportRange" value="range" />
                按 ID 范围导出
              </label>
              <div v-if="exportRange === 'range'" class="range-inputs">
                <div class="input-group">
                  <label>起始 ID</label>
                  <input type="number" v-model.number="exportStartId" min="1" placeholder="起始ID" />
                </div>
                <div class="input-group">
                  <label>结束 ID</label>
                  <input type="number" v-model.number="exportEndId" min="1" placeholder="结束ID" />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="doExport" class="export-btn">
            {{ exportType === 'csv' ? '导出 CSV' : exportType === 'yolo' ? '导出 YOLO' : '导出照片' }}
          </button>
          <button @click="closeExportModal" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import {
  getLabels,
  getLabel,
  updateLabel,
  deleteLabel,
  exportLabels,
  exportYoloLabels,
  exportImages,
  getLabeledImageUrl,
  getAirlines,
  getAircraftTypes
} from '../api'
import BoundingBox from './BoundingBox.vue'

const emit = defineEmits(['refresh'])

const loading = ref(true)
const labels = ref([])
const total = ref(0)
const currentPage = ref(1)
const perPage = ref(20)

// 航司和机型列表
const airlines = ref([])
const aircraftTypes = ref([])

// 模态框
const showModal = ref(false)
const modalMode = ref('view') // 'view' | 'edit'
const selectedLabel = ref(null)
const editForm = ref({})
const saving = ref(false)

// BoundingBox 组件引用
const boundingBoxRef = ref(null)
// 图片尺寸
const imageSize = ref({ width: 1920, height: 1080 })

// 删除确认
const showDeleteConfirm = ref(false)
const labelToDelete = ref(null)
const deleting = ref(false)

// 导出选项
const showExportModal = ref(false)
const exportType = ref('csv') // 'csv' | 'yolo' | 'images'
const exportRange = ref('all') // 'all' | 'range'
const exportStartId = ref(null)
const exportEndId = ref(null)

// 总页数
const totalPages = computed(() => Math.ceil(total.value / perPage.value))

// 解析 YOLO 格式区域字符串为 box 对象
const parseYoloArea = (areaStr, imgWidth, imgHeight) => {
  if (!areaStr) return null
  const parts = areaStr.trim().split(' ').map(parseFloat)
  if (parts.length !== 4) return null
  const [xCenter, yCenter, width, height] = parts
  return {
    x1: (xCenter - width / 2) * imgWidth,
    y1: (yCenter - height / 2) * imgHeight,
    x2: (xCenter + width / 2) * imgWidth,
    y2: (yCenter + height / 2) * imgHeight
  }
}

// 将 box 对象转换为 YOLO 格式区域字符串
const boxToYoloArea = (box, imgWidth, imgHeight) => {
  if (!box) return ''
  const xCenter = ((box.x1 + box.x2) / 2) / imgWidth
  const yCenter = ((box.y1 + box.y2) / 2) / imgHeight
  const width = (box.x2 - box.x1) / imgWidth
  const height = (box.y2 - box.y1) / imgHeight
  return `${xCenter.toFixed(6)} ${yCenter.toFixed(6)} ${width.toFixed(6)} ${height.toFixed(6)}`
}

// 加载图片获取实际尺寸
const loadImageSize = (src) => {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      resolve({ width: img.width, height: img.height })
    }
    img.onerror = () => {
      resolve({ width: 1920, height: 1080 })
    }
    img.src = src
  })
}

// 加载标注列表
const loadLabels = async () => {
  loading.value = true
  try {
    const res = await getLabels(currentPage.value, perPage.value)
    labels.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    console.error('加载标注列表失败:', e)
  } finally {
    loading.value = false
  }
}

// 加载航司和机型
const loadOptions = async () => {
  try {
    const [airlinesRes, typesRes] = await Promise.all([
      getAirlines(),
      getAircraftTypes()
    ])
    airlines.value = airlinesRes.data
    aircraftTypes.value = typesRes.data
  } catch (e) {
    console.error('加载选项失败:', e)
  }
}

// 分页
const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadLabels()
}

// 打开导出对话框
const openExportModal = (type) => {
  exportType.value = type
  exportRange.value = 'all'
  exportStartId.value = null
  exportEndId.value = null
  showExportModal.value = true
}

// 关闭导出对话框
const closeExportModal = () => {
  showExportModal.value = false
}

// 执行导出
const doExport = () => {
  const startId = exportRange.value === 'range' ? exportStartId.value : null
  const endId = exportRange.value === 'range' ? exportEndId.value : null

  if (exportType.value === 'csv') {
    exportLabels(startId, endId)
  } else if (exportType.value === 'yolo') {
    exportYoloLabels(startId, endId)
  } else if (exportType.value === 'images') {
    exportImages(startId, endId)
  }
  closeExportModal()
}

// 导出 CSV
const exportCsv = () => {
  openExportModal('csv')
}

// 导出 YOLO 格式
const exportYolo = () => {
  openExportModal('yolo')
}

// 导出照片
const exportImagesBtn = () => {
  openExportModal('images')
}

// 查看标注
const viewLabel = async (label) => {
  selectedLabel.value = label
  modalMode.value = 'view'
  showModal.value = true

  // 加载图片尺寸
  const imgSrc = getLabeledImageUrl(label.file_name)
  const size = await loadImageSize(imgSrc)
  imageSize.value = size
}

// 编辑标注
const editLabel = async (label) => {
  selectedLabel.value = label

  // 加载图片尺寸
  const imgSrc = getLabeledImageUrl(label.file_name)
  const size = await loadImageSize(imgSrc)
  imageSize.value = size

  // 解析区域
  const box = parseYoloArea(label.registration_area, size.width, size.height)

  editForm.value = {
    typeId: label.type_id,
    typeName: label.type_name,
    airlineId: label.airline_id,
    airlineName: label.airline_name,
    registration: label.registration,
    clarity: label.clarity,
    block: label.block,
    registrationArea: label.registration_area,
    registrationBox: box
  }
  modalMode.value = 'edit'
  showModal.value = true
}

// 机型变更
const onTypeChange = () => {
  const type = aircraftTypes.value.find(t => t.code === editForm.value.typeId)
  editForm.value.typeName = type?.name || ''
}

// 航司变更
const onAirlineChange = () => {
  const airline = airlines.value.find(a => a.code === editForm.value.airlineId)
  editForm.value.airlineName = airline?.name || ''
}

// 画线框更新
const onBoxUpdate = (box) => {
  editForm.value.registrationBox = box
  if (box) {
    editForm.value.registrationArea = boxToYoloArea(box, imageSize.value.width, imageSize.value.height)
  } else {
    editForm.value.registrationArea = ''
  }
}

// 保存编辑
const saveEdit = async () => {
  saving.value = true
  try {
    // 如果有 BoundingBox 组件，从组件获取最新的区域
    let registrationArea = editForm.value.registrationArea
    if (boundingBoxRef.value) {
      const box = boundingBoxRef.value.getRegistrationBox()
      if (box) {
        registrationArea = boxToYoloArea(box, imageSize.value.width, imageSize.value.height)
      }
    }

    await updateLabel(selectedLabel.value.id, {
      type_id: editForm.value.typeId,
      type_name: editForm.value.typeName,
      airline_id: editForm.value.airlineId,
      airline_name: editForm.value.airlineName,
      registration: editForm.value.registration,
      clarity: editForm.value.clarity,
      block: editForm.value.block,
      registration_area: registrationArea
    })
    closeModal()
    loadLabels()
    emit('refresh')
  } catch (e) {
    console.error('保存失败:', e)
    alert(e.response?.data?.error || '保存失败')
  } finally {
    saving.value = false
  }
}

// 关闭模态框
const closeModal = () => {
  showModal.value = false
  selectedLabel.value = null
  editForm.value = {}
}

// 确认删除
const confirmDelete = (label) => {
  labelToDelete.value = label
  showDeleteConfirm.value = true
}

// 执行删除
const doDelete = async () => {
  deleting.value = true
  try {
    await deleteLabel(labelToDelete.value.id)
    cancelDelete()
    loadLabels()
    emit('refresh')
  } catch (e) {
    console.error('删除失败:', e)
    alert(e.response?.data?.error || '删除失败')
  } finally {
    deleting.value = false
  }
}

// 取消删除
const cancelDelete = () => {
  showDeleteConfirm.value = false
  labelToDelete.value = null
}

// 刷新
const refresh = () => {
  loadLabels()
}

defineExpose({ refresh })

onMounted(() => {
  loadLabels()
  loadOptions()
})
</script>

<style scoped>
.label-list {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-header h3 {
  margin: 0;
  color: #fff;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.export-btn,
.refresh-btn {
  padding: 8px 16px;
  border: 1px solid #444;
  border-radius: 4px;
  background: #2a2a2a;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.export-btn:hover,
.refresh-btn:hover {
  background: #3a3a3a;
}

.export-btn {
  background: #2d5a2d;
  border-color: #3d6a3d;
}

.export-btn:hover {
  background: #3d6a3d;
}

.export-btn.yolo {
  background: #4a5a8a;
  border-color: #5a6a9a;
}

.export-btn.yolo:hover {
  background: #5a6a9a;
}

.export-btn.images {
  background: #9c27b0;
  border-color: #ba68c8;
}

.export-btn.images:hover {
  background: #ba68c8;
}

.loading,
.empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
}

.labels-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.labels-table th,
.labels-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #333;
}

.labels-table th {
  background: #252525;
  color: #aaa;
  font-weight: 500;
}

.labels-table td {
  color: #fff;
}

.labels-table td.id-col {
  color: #888;
  font-family: monospace;
}

.labels-table td.filename {
  font-family: monospace;
  color: #4a90d9;
}

.labels-table .actions {
  white-space: nowrap;
}

.labels-table .actions button {
  padding: 4px 10px;
  margin-right: 6px;
  border: none;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
}

.view-btn {
  background: #444;
  color: #fff;
}

.edit-btn {
  background: #4a90d9;
  color: #fff;
}

.delete-btn {
  background: #aa3333;
  color: #fff;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
  padding: 15px 0;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #444;
  border-radius: 4px;
  background: #2a2a2a;
  color: #fff;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination button:hover:not(:disabled) {
  background: #3a3a3a;
}

.page-info {
  color: #888;
  font-size: 14px;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #252525;
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
}

.confirm-modal {
  max-width: 400px;
  padding: 20px;
  text-align: center;
}

.confirm-modal h3 {
  margin: 0 0 15px 0;
  color: #fff;
}

.confirm-modal p {
  color: #aaa;
  margin: 10px 0;
}

.confirm-modal .warning {
  color: #ff6666;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #333;
}

.modal-header h3 {
  margin: 0;
  color: #fff;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 24px;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.preview-section {
  margin-bottom: 20px;
}

.label-info .info-row {
  display: flex;
  margin-bottom: 12px;
}

.label-info .info-row label {
  width: 100px;
  color: #888;
  flex-shrink: 0;
}

.label-info .info-row span {
  color: #fff;
}

.label-info .info-row span.area {
  font-family: monospace;
  color: #4caf50;
}

.edit-form .info-row select,
.edit-form .info-row input:not([type="range"]) {
  flex: 1;
  padding: 8px;
  border: 1px solid #444;
  border-radius: 4px;
  background: #1a1a1a;
  color: #fff;
}

.edit-form .info-row input[type="range"] {
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px 20px;
  border-top: 1px solid #333;
}

.save-btn {
  padding: 8px 20px;
  background: #4a90d9;
  border: none;
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cancel-btn {
  padding: 8px 20px;
  background: #444;
  border: none;
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
}

.confirm-modal .modal-footer {
  justify-content: center;
  border-top: none;
  padding-top: 20px;
}

/* 导出对话框 */
.export-modal {
  max-width: 450px;
}

.export-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  cursor: pointer;
}

.radio-label input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.range-inputs {
  display: flex;
  gap: 15px;
  margin-left: 26px;
  margin-top: 5px;
}

.range-inputs .input-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.range-inputs .input-group label {
  font-size: 12px;
  color: #888;
}

.range-inputs .input-group input {
  width: 120px;
  padding: 8px;
  border: 1px solid #444;
  border-radius: 4px;
  background: #1a1a1a;
  color: #fff;
}

.export-modal .modal-footer .export-btn {
  background: #2d5a2d;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
}

.export-modal .modal-footer .export-btn:hover {
  background: #3d6a3d;
}
</style>
