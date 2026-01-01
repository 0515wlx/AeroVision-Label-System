<template>
  <div class="app">
    <header class="app-header">
      <h1>AeroVision 标注系统</h1>
      <nav class="app-nav">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="{ active: currentTab === tab.id }"
          @click="currentTab = tab.id"
        >
          {{ tab.name }}
        </button>
        <button class="help-btn" @click="showHelp = true" title="操作说明">
          ❓ 帮助
        </button>
        <button class="help-btn">帮助</button>
        <button class="help-btn" @click="showHelp = true" title="操作说明">
          ❓ 帮助
        </button>
      </nav>
    </header>

    <main class="app-main">
      <ImageLabeler
        v-if="currentTab === 'label'"
        @labeled="onLabeled"
      />
      <LabelList
        v-else-if="currentTab === 'list'"
        ref="labelListRef"
        @refresh="onRefresh"
      />
      <StatsPanel

    <!-- 操作说明弹窗 -->
    <HelpModal :show="showHelp" @close="showHelp = false" />
        v-else-if="currentTab === 'stats'"
        ref="statsPanelRef"
      />
    </main>
import { ref, onMounted } from 'vue'
    <!-- 操作说明弹窗 -->
    <HelpModal :show="showHelp" @close="showHelp = false" />
  </div>
import HelpModal from './components/HelpModal.vue'
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ImageLabeler from './components/ImageLabeler.vue'
import LabelList from './components/LabelList.vue'
import StatsPanel from './components/StatsPanel.vue'
import HelpModal from './components/HelpModal.vue'

const tabs = [
const showHelp = ref(false)
  { id: 'label', name: '标注' },
  { id: 'list', name: '已标注' },
  { id: 'stats', name: '统计' }
]

const currentTab = ref('label')
const labelListRef = ref(null)
const statsPanelRef = ref(null)
const showHelp = ref(false)


// 首次访问时显示帮助
onMounted(() => {
  const hideHelp = localStorage.getItem('hideHelpModal')
  if (!hideHelp) {
    showHelp.value = true
  }
})
// 标注完成后刷新统计
const onLabeled = () => {
  statsPanelRef.value?.refresh()
}

// 列表刷新后刷新统计
const onRefresh = () => {
  statsPanelRef.value?.refresh()
}

// 首次访问时显示帮助
onMounted(() => {
  const hideHelp = localStorage.getItem('hideHelpModal')
  if (!hideHelp) {
    showHelp.value = true
  }
})
</script>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1a1a1a;
  color: #fff;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
  background: #252525;
  border-bottom: 1px solid #333;
}

.app-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #4a90d9;
}

.app-nav {
  display: flex;
  gap: 5px;
}

.app-nav button {
  border: none;
  color: #fff;

.help-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #4a90d9;
  color: #fff;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.2s;
}

.help-btn:hover {
  background: #357ab8;
}
}

.help-btn {
  margin-left: 10px;
  padding: 10px 16px !important;
  background: #2d5a2d !important;
  color: #8fdf8f !important;
}

.help-btn:hover {
  background: #3d6a3d !important;
  color: #fff !important;
  background: transparent;
  color: #888;
  font-size: 14px;
  cursor: pointer;
  border-radius: 4px;
  overflow: hidden;
}

.app-nav button:hover {
  color: #fff;
  background: #333;
}

.app-nav button.active {
  color: #fff;
  background: #4a90d9;
}

.app-main {
  flex: 1;
  padding: 20px;
  overflow: auto;
}

.help-btn {
  padding: 10px;
  border: none;
  background: transparent;
  color: #888;
  font-size: 14px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.help-btn:hover {
  color: #fff;
  background: #333;
}
</style>
