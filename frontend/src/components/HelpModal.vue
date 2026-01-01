<template>
  <div v-if="show" class="help-modal-overlay" @click.self="close">
    <div class="help-modal">
      <div class="help-header">
        <h2>📖 操作说明</h2>
        <button class="close-btn" @click="close">×</button>
      </div>

      <div class="help-content">
        <section>
          <h3>🎯 基本操作</h3>
          <ul>
            <li><strong>选择图片</strong>：系统自动加载待标注图片</li>
            <li><strong>绘制区域</strong>：在图片上按住鼠标左键拖动，框选机身注册号区域</li>
            <li><strong>填写信息</strong>：选择机型、航司，输入注册号，调整清晰度和遮挡度</li>
            <li><strong>保存标注</strong>：填写完整后点击"保存标注"按钮</li>
          </ul>
        </section>

        <section>
          <h3>⏭️ 跳过功能</h3>
          <ul>
            <li><strong>跳过此图</strong>：将图片标记为废图并永久隐藏，适用于无法标注的图片（如模糊、错误、不相关等）</li>
            <li>跳过的图片不会再次显示在待标注列表中</li>
            <li>废图统计会显示在"统计"页面中</li>
            <li>跳过操作需要确认，避免误操作</li>
          </ul>
        </section>

        <section>
          <h3>🔒 协作功能</h3>
          <ul>
            <li>系统会自动锁定正在标注的图片，防止他人同时标注</li>
            <li>锁定超时时间为 10 分钟，超时后自动释放</li>
            <li>如果图片被他人锁定，系统会自动跳到下一张</li>
          </ul>
        </section>

        <section>
          <h3>📊 统计与导出</h3>
          <ul>
            <li><strong>查看统计</strong>：在"统计"页面查看已标注、待标注、已跳过数量及分布</li>
            <li><strong>导出数据</strong>：
              <ul>
                <li>导出标注数据 (CSV)：标注信息表格</li>
                <li>导出标注数据 (YOLO)：YOLO 格式的标注文件</li>
                <li>导出航司配置：当前系统中的航司列表</li>
                <li>导出机型配置：当前系统中的机型列表</li>
              </ul>
            </li>
          </ul>
        </section>

        <section>
          <h3>⌨️ 快捷提示</h3>
          <ul>
            <li>标注时确保注册号区域框选准确</li>
            <li>清晰度和遮挡度可以通过滑块快速调整</li>
            <li>如需添加新的机型或航司，在下拉菜单中选择"+ 新增"选项</li>
            <li>标注完成后会自动跳到下一张图片</li>
          </ul>
        </section>

        <section>
          <h3>📝 文件命名规则</h3>
          <ul>
            <li>标注后的文件格式：<code>{机型代码}-{序号}.{扩展名}</code></li>
            <li>例如：<code>A320-0001.jpg</code>、<code>B738-0042.png</code></li>
            <li>序号从 0001 开始，每个机型独立计数</li>
          </ul>
        </section>
      </div>

      <div class="help-footer">
        <label class="no-show-checkbox">
          <input type="checkbox" v-model="dontShowAgain" />
          不再显示此提示
        </label>
        <button class="ok-btn" @click="close">我知道了</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['close'])

const dontShowAgain = ref(false)

const close = () => {
  if (dontShowAgain.value) {
    localStorage.setItem('hideHelpModal', 'true')
  }
  emit('close')
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    dontShowAgain.value = false
  }
})
</script>

<style scoped>
.help-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.help-modal {
  background: #252525;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.help-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 30px;
  border-bottom: 1px solid #333;
}

.help-header h2 {
  margin: 0;
  color: #fff;
  font-size: 24px;
  font-weight: 500;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #333;
  color: #aaa;
  font-size: 24px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #444;
  color: #fff;
}

.help-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px 30px;
}

.help-content section {
  margin-bottom: 28px;
}

.help-content section:last-child {
  margin-bottom: 0;
}

.help-content h3 {
  margin: 0 0 12px 0;
  color: #4a90d9;
  font-size: 18px;
  font-weight: 500;
}

.help-content ul {
  margin: 0;
  padding-left: 24px;
  color: #ccc;
  line-height: 1.8;
}

.help-content ul ul {
  margin-top: 8px;
}

.help-content li {
  margin-bottom: 8px;
}

.help-content li:last-child {
  margin-bottom: 0;
}

.help-content strong {
  color: #fff;
  font-weight: 500;
}

.help-content code {
  background: #1a1a1a;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #4caf50;
}

.help-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 30px;
  border-top: 1px solid #333;
}

.no-show-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #aaa;
  font-size: 14px;
  cursor: pointer;
  user-select: none;
}

.no-show-checkbox input[type="checkbox"] {
  cursor: pointer;
}

.ok-btn {
  padding: 10px 32px;
  border: none;
  border-radius: 6px;
  background: #4a90d9;
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.ok-btn:hover {
  background: #5a9fe9;
}

/* 滚动条样式 */
.help-content::-webkit-scrollbar {
  width: 8px;
}

.help-content::-webkit-scrollbar-track {
  background: #1a1a1a;
  border-radius: 4px;
}

.help-content::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}

.help-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
