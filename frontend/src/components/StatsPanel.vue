<template>
  <div class="stats-panel">
    <h3>标注统计</h3>

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
        <div class="stat-card">
          <div class="stat-value">{{ totalImages }}</div>
          <div class="stat-label">总计</div>
        </div>
        <div class="stat-card progress-card">
          <div class="stat-value">{{ progressPercent }}%</div>
          <div class="stat-label">完成率</div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- 按机型统计 -->
      <div class="stats-section">
        <h4>按机型统计 (Top 10)</h4>
        <div v-if="Object.keys(stats.by_type || {}).length === 0" class="no-data">
          暂无数据
        </div>
        <div v-else class="stats-bars">
          <div
            v-for="(count, typeId) in topTypes"
            :key="typeId"
            class="bar-item"
          >
            <div class="bar-label">{{ typeId }}</div>
            <div class="bar-track">
              <div
                class="bar-fill type"
                :style="{ width: getBarWidth(count, maxTypeCount) + '%' }"
              ></div>
            </div>
            <div class="bar-count">{{ count }}</div>
          </div>
        </div>
      </div>

      <!-- 按航司统计 -->
      <div class="stats-section">
        <h4>按航司统计 (Top 10)</h4>
        <div v-if="Object.keys(stats.by_airline || {}).length === 0" class="no-data">
          暂无数据
        </div>
        <div v-else class="stats-bars">
          <div
            v-for="(count, airlineId) in topAirlines"
            :key="airlineId"
            class="bar-item"
          >
            <div class="bar-label">{{ airlineId }}</div>
            <div class="bar-track">
              <div
                class="bar-fill airline"
                :style="{ width: getBarWidth(count, maxAirlineCount) + '%' }"
              ></div>
            </div>
            <div class="bar-count">{{ count }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getStats } from '../api'

const loading = ref(true)
const stats = ref({
  total_labeled: 0,
  unlabeled: 0,
  by_type: {},
  by_airline: {}
})

// 总图片数
const totalImages = computed(() => stats.value.total_labeled + stats.value.unlabeled)

// 完成率
const progressPercent = computed(() => {
  if (totalImages.value === 0) return 0
  return Math.round((stats.value.total_labeled / totalImages.value) * 100)
})

// Top 10 机型
const topTypes = computed(() => {
  const sorted = Object.entries(stats.value.by_type || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
  return Object.fromEntries(sorted)
})

// Top 10 航司
const topAirlines = computed(() => {
  const sorted = Object.entries(stats.value.by_airline || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
  return Object.fromEntries(sorted)
})

// 最大机型数量
const maxTypeCount = computed(() => {
  const values = Object.values(stats.value.by_type || {})
  return values.length > 0 ? Math.max(...values) : 1
})

// 最大航司数量
const maxAirlineCount = computed(() => {
  const values = Object.values(stats.value.by_airline || {})
  return values.length > 0 ? Math.max(...values) : 1
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

.stats-panel h3 {
  margin: 0 0 20px 0;
  color: #fff;
  font-size: 18px;
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
  margin-bottom: 30px;
}

.stat-card {
  background: #1a1a1a;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #4a90d9;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #888;
}

.progress-card {
  position: relative;
}

.progress-card .stat-value {
  color: #4caf50;
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

.stats-section {
  margin-bottom: 25px;
}

.stats-section h4 {
  margin: 0 0 15px 0;
  color: #aaa;
  font-size: 14px;
  font-weight: 500;
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
