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
        v-else-if="currentTab === 'stats'"
        ref="statsPanelRef"
      />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ImageLabeler from './components/ImageLabeler.vue'
import LabelList from './components/LabelList.vue'
import StatsPanel from './components/StatsPanel.vue'

const tabs = [
  { id: 'label', name: '标注' },
  { id: 'list', name: '已标注' },
  { id: 'stats', name: '统计' }
]

const currentTab = ref('label')
const labelListRef = ref(null)
const statsPanelRef = ref(null)

// 标注完成后刷新统计
const onLabeled = () => {
  statsPanelRef.value?.refresh()
}

// 列表刷新后刷新统计
const onRefresh = () => {
  statsPanelRef.value?.refresh()
}
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
  padding: 10px 20px;
  border: none;
  background: transparent;
  color: #888;
  font-size: 14px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
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
</style>
