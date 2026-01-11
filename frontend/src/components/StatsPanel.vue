<template>
  <div class="stats-panel">
    <div class="stats-header">
      <h3>标注统计</h3>
      <div class="header-actions">
        <button @click="exportAirlines" class="export-btn airline">
          导出航司 JSON
        </button>
        <button @click="exportAircraftTypes" class="export-btn type">
          导出机型 JSON
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else class="stats-content">
      <!-- 总览 -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_labeled }}</div>
          <div class="stat-label">已标注</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.unlabeled }}</div>
          <div class="stat-label">待标注</div>
        </div>
        <div class="stat-card skipped">
          <div class="stat-value">{{ stats.skipped_count || 0 }}</div>
          <div class="stat-label">废图</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ progressPercent }}%</div>
          <div class="stat-label">完成率</div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- 搜索框 -->
      <div class="search-section">
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索机型或航司（代码或名称）..."
        />
      </div>

      <!-- 搜索结果 -->
      <div v-if="searchQuery" class="search-results">
        <h4>搜索结果</h4>
        <div v-if="filteredTypes.length === 0 && filteredAirlines.length === 0" class="no-data">
          未找到匹配结果
        </div>
        <div v-else>
          <div v-if="filteredTypes.length > 0" class="result-group">
            <div class="result-label">机型</div>
            <div class="result-list">
              <div v-for="item in filteredTypes" :key="item.code" class="result-item">
                <span class="result-code">{{ item.code }}</span>
                <span class="result-name">{{ item.name }}</span>
                <span class="result-count">{{ item.count }} 张</span>
              </div>
            </div>
          </div>
          <div v-if="filteredAirlines.length > 0" class="result-group">
            <div class="result-label">航司</div>
            <div class="result-list">
              <div v-for="item in filteredAirlines" :key="item.code" class="result-item">
                <span class="result-code">{{ item.code }}</span>
                <span class="result-name">{{ item.name }}</span>
                <span class="result-count">{{ item.count }} 张</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 按机型统计 -->
      <div class="stats-section">
        <div class="section-header">
          <h4>按机型统计 ({{ typesDetail.length }} 种)</h4>
          <button v-if="typesDetail.length > 10" @click="showAllTypes = !showAllTypes" class="toggle-btn">
            {{ showAllTypes ? '收起' : '展开全部' }}
          </button>
        </div>
        <div v-if="typesDetail.length === 0" class="no-data">
          暂无数据
        </div>
        <div v-else class="stats-bars">
          <div
            v-for="item in displayedTypes"
            :key="item.code"
            class="bar-item"
          >
            <div class="bar-label" :title="item.name">{{ item.code }}</div>
            <div class="bar-track">
              <div
                class="bar-fill type"
                :style="{ width: getBarWidth(item.count, maxTypeCount) + '%' }"
              ></div>
            </div>
            <div class="bar-count">{{ item.count }}</div>
          </div>
        </div>
      </div>

      <!-- 按航司统计 -->
      <div class="stats-section">
        <div class="section-header">
          <h4>按航司统计 ({{ airlinesDetail.length }} 家)</h4>
          <button v-if="airlinesDetail.length > 10" @click="showAllAirlines = !showAllAirlines" class="toggle-btn">
            {{ showAllAirlines ? '收起' : '展开全部' }}
          </button>
        </div>
        <div v-if="airlinesDetail.length === 0" class="no-data">
          暂无数据
        </div>
        <div v-else class="stats-bars">
          <div
            v-for="item in displayedAirlines"
            :key="item.code"
            class="bar-item"
          >
            <div class="bar-label" :title="item.name">{{ item.code }}</div>
            <div class="bar-track">
              <div
                class="bar-fill airline"
                :style="{ width: getBarWidth(item.count, maxAirlineCount) + '%' }"
              ></div>
            </div>
            <div class="bar-count">{{ item.count }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getStats, exportAirlines, exportAircraftTypes } from '../api'

const loading = ref(true)
const searchQuery = ref('')
const showAllTypes = ref(false)
const showAllAirlines = ref(false)

const stats = ref({
  total_labeled: 0,
  unlabeled: 0,
  skipped_count: 0,
  by_type: {},
  by_airline: {},
  types_detail: [],
  airlines_detail: []
})

// 总图片数（已标注 + 待标注，不含废图）
const totalImages = computed(() => stats.value.total_labeled + stats.value.unlabeled)

// 完成率
const progressPercent = computed(() => {
  if (totalImages.value === 0) return 0
  return Math.round((stats.value.total_labeled / totalImages.value) * 100)
})

// 机型详情列表
const typesDetail = computed(() => stats.value.types_detail || [])

// 航司详情列表
const airlinesDetail = computed(() => stats.value.airlines_detail || [])

// 显示的机型（展开或只显示 Top 10）
const displayedTypes = computed(() => {
  return showAllTypes.value ? typesDetail.value : typesDetail.value.slice(0, 10)
})

// 显示的航司（展开或只显示 Top 10）
const displayedAirlines = computed(() => {
  return showAllAirlines.value ? airlinesDetail.value : airlinesDetail.value.slice(0, 10)
})

// 搜索过滤机型
const filteredTypes = computed(() => {
  if (!searchQuery.value) return []
  const query = searchQuery.value.toLowerCase()
  return typesDetail.value.filter(item =>
    item.code.toLowerCase().includes(query) ||
    item.name.toLowerCase().includes(query)
  )
})

// 搜索过滤航司
const filteredAirlines = computed(() => {
  if (!searchQuery.value) return []
  const query = searchQuery.value.toLowerCase()
  return airlinesDetail.value.filter(item =>
    item.code.toLowerCase().includes(query) ||
    item.name.toLowerCase().includes(query)
  )
})

// 最大机型数量
const maxTypeCount = computed(() => {
  if (typesDetail.value.length === 0) return 1
  return Math.max(...typesDetail.value.map(item => item.count))
})

// 最大航司数量
const maxAirlineCount = computed(() => {
  if (airlinesDetail.value.length === 0) return 1
  return Math.max(...airlinesDetail.value.map(item => item.count))
})

// 计算条形图宽度
const getBarWidth = (count, max) => {
  if (max === 0) return 0
  return Math.round((count / max) * 100)
}

// 加载统计数据
const loadStats = async () => {
  loading.value = true
  try {
    const res = await getStats()
    stats.value = res.data
  } catch (e) {
    console.error('加载统计数据失败:', e)
  } finally {
    loading.value = false
  }
}

// 刷新
const refresh = () => {
  loadStats()
}

defineExpose({ refresh })

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.stats-panel {
  padding: 20px;
  background: #252525;
  border-radius: 8px;
  height: 100%;
  overflow: auto;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stats-panel h3 {
  margin: 0;
  color: #fff;
  font-size: 18px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.export-btn {
  padding: 8px 16px;
  border: 1px solid #444;
  border-radius: 4px;
  background: #2a2a2a;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.export-btn:hover {
  background: #3a3a3a;
}

.export-btn.airline {
  background: #ff9800;
  border-color: #ffa726;
}

.export-btn.airline:hover {
  background: #ffa726;
}

.export-btn.type {
  background: #4a90d9;
  border-color: #6aaced;
}

.export-btn.type:hover {
  background: #6aaced;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #888;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: #1a1a1a;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  position: relative;
}

.stat-card.skipped .stat-value {
  color: #f44336;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #4a90d9;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #888;
}

.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: #333;
  border-radius: 0 0 8px 8px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #8bc34a);
  transition: width 0.5s ease;
}

/* 搜索框 */
.search-section {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #444;
  border-radius: 6px;
  background: #1a1a1a;
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #4a90d9;
}

.search-input::placeholder {
  color: #666;
}

/* 搜索结果 */
.search-results {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.search-results h4 {
  margin: 0 0 10px 0;
  color: #fff;
  font-size: 14px;
}

.result-group {
  margin-bottom: 15px;
}

.result-group:last-child {
  margin-bottom: 0;
}

.result-label {
  color: #888;
  font-size: 12px;
  margin-bottom: 8px;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #252525;
  border-radius: 4px;
}

.result-code {
  font-family: monospace;
  color: #4a90d9;
  min-width: 60px;
}

.result-name {
  flex: 1;
  color: #ccc;
  font-size: 13px;
}

.result-count {
  color: #888;
  font-size: 13px;
}

/* 统计区域 */
.stats-section {
  margin-bottom: 25px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.stats-section h4 {
  margin: 0;
  color: #aaa;
  font-size: 14px;
  font-weight: 500;
}

.toggle-btn {
  padding: 4px 10px;
  border: 1px solid #444;
  border-radius: 4px;
  background: transparent;
  color: #888;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.toggle-btn:hover {
  border-color: #666;
  color: #fff;
}

.no-data {
  color: #666;
  font-size: 14px;
  padding: 20px;
  text-align: center;
}

.stats-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-label {
  width: 60px;
  font-size: 13px;
  color: #aaa;
  font-family: monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bar-track {
  flex: 1;
  height: 20px;
  background: #1a1a1a;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.bar-fill.type {
  background: linear-gradient(90deg, #4a90d9, #6aaced);
}

.bar-fill.airline {
  background: linear-gradient(90deg, #ff9800, #ffc107);
}

.bar-count {
  width: 40px;
  font-size: 13px;
  color: #fff;
  text-align: right;
}
</style>
