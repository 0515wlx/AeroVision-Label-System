<template>
  <div class="bounding-box-container" ref="containerRef">
    <canvas
      ref="canvasRef"
      :width="canvasWidth"
      :height="canvasHeight"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseUp"
    ></canvas>
    <div class="box-legend">
      <span class="legend-item airplane">
        <span class="legend-color"></span>
        机身区域 ({{ airplaneBox ? '已绘制' : '未绘制' }})
      </span>
      <span class="legend-item registration">
        <span class="legend-color"></span>
        注册号区域 ({{ registrationBox ? '已绘制' : '未绘制' }})
      </span>
    </div>
    <div class="box-controls">
      <button @click="setMode('airplane')" :class="{ active: currentMode === 'airplane' }">
        绘制机身
      </button>
      <button @click="setMode('registration')" :class="{ active: currentMode === 'registration' }">
        绘制注册号
      </button>
      <button @click="clearBoxes" class="clear-btn">清除全部</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'

const props = defineProps({
  imageSrc: String,
  imageWidth: Number,
  imageHeight: Number,
  initialAirplaneBox: Object,
  initialRegistrationBox: Object
})

const emit = defineEmits(['update:airplaneBox', 'update:registrationBox'])

const containerRef = ref(null)
const canvasRef = ref(null)
const canvasWidth = ref(800)
const canvasHeight = ref(600)

const currentMode = ref('airplane') // 'airplane' | 'registration'
const isDrawing = ref(false)
const startPoint = ref(null)
const currentPoint = ref(null)

const airplaneBox = ref(props.initialAirplaneBox || null)
const registrationBox = ref(props.initialRegistrationBox || null)

const image = ref(null)
const scale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)

// 加载图片
const loadImage = () => {
  if (!props.imageSrc) return

  const img = new Image()
  img.onload = () => {
    image.value = img

    // 计算缩放比例，使图片适应画布
    const containerWidth = containerRef.value?.clientWidth || 800
    const containerHeight = 600

    canvasWidth.value = containerWidth
    canvasHeight.value = containerHeight

    const scaleX = containerWidth / img.width
    const scaleY = containerHeight / img.height
    scale.value = Math.min(scaleX, scaleY, 1)

    // 居中显示
    offsetX.value = (containerWidth - img.width * scale.value) / 2
    offsetY.value = (containerHeight - img.height * scale.value) / 2

    nextTick(() => {
      draw()
    })
  }
  img.src = props.imageSrc
}

// 绘制画布
const draw = () => {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)

  // 绘制图片
  if (image.value) {
    ctx.drawImage(
      image.value,
      offsetX.value,
      offsetY.value,
      image.value.width * scale.value,
      image.value.height * scale.value
    )
  }

  // 绘制机身框
  if (airplaneBox.value) {
    drawBox(ctx, airplaneBox.value, '#00ff00', '机身')
  }

  // 绘制注册号框
  if (registrationBox.value) {
    drawBox(ctx, registrationBox.value, '#ff6600', '注册号')
  }

  // 绘制当前正在绘制的框
  if (isDrawing.value && startPoint.value && currentPoint.value) {
    const color = currentMode.value === 'airplane' ? '#00ff00' : '#ff6600'
    drawTempBox(ctx, startPoint.value, currentPoint.value, color)
  }
}

// 绘制矩形框
const drawBox = (ctx, box, color, label) => {
  const x1 = box.x1 * scale.value + offsetX.value
  const y1 = box.y1 * scale.value + offsetY.value
  const x2 = box.x2 * scale.value + offsetX.value
  const y2 = box.y2 * scale.value + offsetY.value

  ctx.strokeStyle = color
  ctx.lineWidth = 2
  ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)

  // 半透明填充
  ctx.fillStyle = color + '20'
  ctx.fillRect(x1, y1, x2 - x1, y2 - y1)

  // 标签
  ctx.fillStyle = color
  ctx.font = '14px sans-serif'
  ctx.fillText(label, x1 + 4, y1 + 16)
}

// 绘制临时框
const drawTempBox = (ctx, start, end, color) => {
  ctx.strokeStyle = color
  ctx.lineWidth = 2
  ctx.setLineDash([5, 5])
  ctx.strokeRect(start.x, start.y, end.x - start.x, end.y - start.y)
  ctx.setLineDash([])
}

// 将画布坐标转换为图片坐标
const canvasToImage = (canvasX, canvasY) => {
  const imageX = (canvasX - offsetX.value) / scale.value
  const imageY = (canvasY - offsetY.value) / scale.value
  return { x: imageX, y: imageY }
}

// 鼠标事件处理
const handleMouseDown = (e) => {
  const rect = canvasRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  isDrawing.value = true
  startPoint.value = { x, y }
  currentPoint.value = { x, y }
}

const handleMouseMove = (e) => {
  if (!isDrawing.value) return

  const rect = canvasRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  currentPoint.value = { x, y }
  draw()
}

const handleMouseUp = () => {
  if (!isDrawing.value || !startPoint.value || !currentPoint.value) {
    isDrawing.value = false
    return
  }

  // 转换为图片坐标
  const start = canvasToImage(startPoint.value.x, startPoint.value.y)
  const end = canvasToImage(currentPoint.value.x, currentPoint.value.y)

  // 确保坐标在图片范围内
  const imgWidth = props.imageWidth || image.value?.width || 1920
  const imgHeight = props.imageHeight || image.value?.height || 1080

  const box = {
    x1: Math.max(0, Math.min(start.x, end.x)),
    y1: Math.max(0, Math.min(start.y, end.y)),
    x2: Math.min(imgWidth, Math.max(start.x, end.x)),
    y2: Math.min(imgHeight, Math.max(start.y, end.y))
  }

  // 检查框是否有效（宽高大于10像素）
  if (box.x2 - box.x1 > 10 && box.y2 - box.y1 > 10) {
    if (currentMode.value === 'airplane') {
      airplaneBox.value = box
      emit('update:airplaneBox', box)
    } else {
      registrationBox.value = box
      emit('update:registrationBox', box)
    }
  }

  isDrawing.value = false
  startPoint.value = null
  currentPoint.value = null
  draw()
}

// 设置绘制模式
const setMode = (mode) => {
  currentMode.value = mode
}

// 清除所有框
const clearBoxes = () => {
  airplaneBox.value = null
  registrationBox.value = null
  emit('update:airplaneBox', null)
  emit('update:registrationBox', null)
  draw()
}

// 计算 YOLO 格式的区域字符串
const calculateArea = (box, imgWidth, imgHeight) => {
  if (!box) return ''

  const xCenter = ((box.x1 + box.x2) / 2) / imgWidth
  const yCenter = ((box.y1 + box.y2) / 2) / imgHeight
  const width = (box.x2 - box.x1) / imgWidth
  const height = (box.y2 - box.y1) / imgHeight

  return `${xCenter.toFixed(4)} ${yCenter.toFixed(4)} ${width.toFixed(4)} ${height.toFixed(4)}`
}

// 暴露方法给父组件
defineExpose({
  calculateArea,
  getAirplaneBox: () => airplaneBox.value,
  getRegistrationBox: () => registrationBox.value
})

// 监听图片变化
watch(() => props.imageSrc, () => {
  airplaneBox.value = null
  registrationBox.value = null
  loadImage()
})

// 监听初始值变化
watch(() => props.initialAirplaneBox, (val) => {
  airplaneBox.value = val
  draw()
})

watch(() => props.initialRegistrationBox, (val) => {
  registrationBox.value = val
  draw()
})

onMounted(() => {
  loadImage()
})
</script>

<style scoped>
.bounding-box-container {
  position: relative;
  width: 100%;
}

canvas {
  display: block;
  background: #1a1a1a;
  border: 1px solid #333;
  cursor: crosshair;
}

.box-legend {
  display: flex;
  gap: 20px;
  margin-top: 10px;
  font-size: 14px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 2px;
}

.legend-item.airplane .legend-color {
  background: #00ff00;
}

.legend-item.registration .legend-color {
  background: #ff6600;
}

.box-controls {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.box-controls button {
  padding: 8px 16px;
  border: 1px solid #444;
  background: #2a2a2a;
  color: #fff;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.box-controls button:hover {
  background: #3a3a3a;
}

.box-controls button.active {
  background: #4a90d9;
  border-color: #4a90d9;
}

.box-controls .clear-btn {
  margin-left: auto;
  background: #aa3333;
  border-color: #aa3333;
}

.box-controls .clear-btn:hover {
  background: #cc4444;
}
</style>
