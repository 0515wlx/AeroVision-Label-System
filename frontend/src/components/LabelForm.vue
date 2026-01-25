<template>
  <form class="label-form" @submit.prevent="handleSubmit">
    <h3>标注信息</h3>

    <!-- AI 预测提示 -->
    <div v-if="aiPrediction" class="ai-prediction-banner">
      <span class="ai-badge">AI 预测</span>
      <span v-if="aiPrediction.is_new_class" class="new-class-badge">可能是新类别</span>
    </div>

    <!-- AI 预测展示 - 机型 -->
    <div v-if="aiPrediction" class="model-prediction">
      <label>AI 预测（机型）</label>
      <div class="prediction-card">
        <div class="top1">
          <span class="class-name">{{ aiPrediction.aircraft_class }}</span>
          <span class="confidence" :class="getConfidenceClass(aiPrediction.aircraft_confidence)">
            {{ (aiPrediction.aircraft_confidence * 100).toFixed(1) }}%
          </span>
        </div>
        <div v-if="aiPrediction.aircraft_confidence < 0.8" class="warning">
          置信度较低，请仔细确认
        </div>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="useModelType"
            @change="onUseModelTypeChange"
          />
          使用预测结果
        </label>
      </div>
    </div>

    <!-- AI 预测展示 - 航司 -->
    <div v-if="aiPrediction" class="model-prediction">
      <label>AI 预测（航司）</label>
      <div class="prediction-card">
        <div class="top1">
          <span class="class-name">{{ aiPrediction.airline_class }}</span>
          <span class="confidence" :class="getConfidenceClass(aiPrediction.airline_confidence)">
            {{ (aiPrediction.airline_confidence * 100).toFixed(1) }}%
          </span>
        </div>
        <div v-if="aiPrediction.airline_confidence < 0.8" class="warning">
          置信度较低，请仔细确认
        </div>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="useModelAirline"
            @change="onUseModelAirlineChange"
          />
          使用预测结果
        </label>
      </div>
    </div>

    <!-- AI 预测展示 - 注册号（OCR） -->
    <div v-if="aiPrediction && aiPrediction.registration" class="model-prediction">
      <label>AI 识别（注册号）</label>
      <div class="prediction-card">
        <div class="ocr-result">
          <span class="text">{{ aiPrediction.registration }}</span>
          <span class="confidence" :class="getConfidenceClass(aiPrediction.registration_confidence)">
            {{ (aiPrediction.registration_confidence * 100).toFixed(1) }}%
          </span>
        </div>
        <div v-if="aiPrediction.registration_confidence < 0.7" class="warning">
          识别置信度较低，请仔细确认
        </div>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="useModelOcr"
            @change="onUseModelOcrChange"
          />
          使用识别结果
        </label>
      </div>
    </div>

    <!-- AI 预测展示 - 质量评估 -->
    <div v-if="aiPrediction" class="model-prediction quality-prediction">
      <label>AI 质量评估</label>
      <div class="prediction-card">
        <div class="quality-row">
          <span>清晰度:</span>
          <span class="quality-value">{{ (aiPrediction.clarity * 100).toFixed(0) }}%</span>
          <span>遮挡度:</span>
          <span class="quality-value">{{ (aiPrediction.block * 100).toFixed(0) }}%</span>
        </div>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="useModelQuality"
            @change="onUseModelQualityChange"
          />
          使用质量评估
        </label>
      </div>
    </div>

    <!-- 航司选择 -->
    <div class="form-group" :class="{ disabled: useModelAirline }">
      <label>航司</label>
      <div class="select-with-add">
        <select
          v-model="form.airlineId"
          @change="onAirlineChange"
          :disabled="useModelAirline"
        >
          <option value="">请选择航司</option>
          <option v-for="airline in airlines" :key="airline.code" :value="airline.code">
            {{ airline.code }} - {{ airline.name }}
          </option>
          <option value="__new__">+ 新增航司</option>
        </select>
      </div>
      <div v-if="showNewAirline" class="new-item-form">
        <input v-model="newAirline.code" placeholder="航司代码 (如 CCA)" maxlength="10" />
        <input v-model="newAirline.name" placeholder="航司名称" />
        <button type="button" @click="addAirline">添加</button>
        <button type="button" @click="cancelNewAirline">取消</button>
      </div>
    </div>

    <!-- 机型选择 -->
    <div class="form-group" :class="{ disabled: useModelType }">
      <label>机型</label>
      <div class="select-with-add">
        <select
          v-model="form.typeId"
          @change="onTypeChange"
          :disabled="useModelType"
        >
          <option value="">请选择机型</option>
          <option v-for="type in aircraftTypes" :key="type.code" :value="type.code">
            {{ type.code }} - {{ type.name }}
          </option>
          <option value="__new__">+ 新增机型</option>
        </select>
      </div>
      <div v-if="showNewType" class="new-item-form">
        <input v-model="newType.code" placeholder="机型代码 (如 A320)" maxlength="10" />
        <input v-model="newType.name" placeholder="机型名称" />
        <button type="button" @click="addType">添加</button>
        <button type="button" @click="cancelNewType">取消</button>
      </div>
    </div>

    <!-- 注册号 -->
    <div class="form-group" :class="{ disabled: useModelOcr }">
      <label>注册号</label>
      <input
        v-model="form.registration"
        placeholder="如 B-1234"
        maxlength="20"
        :disabled="useModelOcr"
      />
    </div>

    <!-- 清晰度 -->
    <div class="form-group">
      <label>清晰度: {{ form.clarity.toFixed(2) }}</label>
      <input
        type="range"
        v-model.number="form.clarity"
        min="0"
        max="1"
        step="0.01"
      />
      <div class="range-labels">
        <span>模糊</span>
        <span>清晰</span>
      </div>
    </div>

    <!-- 遮挡度 -->
    <div class="form-group">
      <label>遮挡度: {{ form.block.toFixed(2) }}</label>
      <input
        type="range"
        v-model.number="form.block"
        min="0"
        max="1"
        step="0.01"
      />
      <div class="range-labels">
        <span>无遮挡</span>
        <span>完全遮挡</span>
      </div>
    </div>

    <!-- 区域信息显示 -->
    <div class="form-group area-info">
      <label>区域信息</label>
      <div class="area-display">
        <div :class="{ valid: !!registrationArea }">
          注册号: {{ registrationArea || '未绘制' }}
        </div>
      </div>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- 提交按钮 -->
    <div class="form-actions">
      <button type="submit" :disabled="!isValid || loading" class="submit-btn">
        {{ loading ? '保存中...' : '保存标注' }}
      </button>
      <button type="button" @click="handleSkip" class="skip-btn">
        跳过
      </button>
      <button type="button" @click="handleSkipAsInvalid" class="skip-invalid-btn">
        废图
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { getAirlines, getAircraftTypes, createAirline, createAircraftType } from '../api'

const props = defineProps({
  registrationArea: String,
  initialData: Object,
  currentImage: Object  // 包含 ai_prediction 字段
})

const emit = defineEmits(['submit', 'skip', 'skipAsInvalid'])

const airlines = ref([])
const aircraftTypes = ref([])
const loading = ref(false)
const error = ref('')

// AI 预测数据（从 currentImage 中获取）
const aiPrediction = computed(() => {
  return props.currentImage?.ai_prediction || null
})

// 是否使用模型预测
const useModelType = ref(false)
const useModelAirline = ref(false)
const useModelOcr = ref(false)
const useModelQuality = ref(false)

const form = ref({
  airlineId: '',
  airlineName: '',
  typeId: '',
  typeName: '',
  registration: '',
  clarity: 0.8,
  block: 0
})

// 新增航司
const showNewAirline = ref(false)
const newAirline = ref({ code: '', name: '' })

// 新增机型
const showNewType = ref(false)
const newType = ref({ code: '', name: '' })

// 置信度样式
const getConfidenceClass = (confidence) => {
  if (confidence >= 0.95) return 'high'
  if (confidence >= 0.8) return 'medium'
  return 'low'
}

// 表单验证
const isValid = computed(() => {
  return (
    form.value.airlineId &&
    form.value.typeId &&
    form.value.registration &&
    props.registrationArea
  )
})

// 监听当前图片变化，重置使用状态
watch(() => props.currentImage, (newImage) => {
  if (newImage) {
    // 重置使用状态
    useModelType.value = false
    useModelAirline.value = false
    useModelOcr.value = false
    useModelQuality.value = false

    // 如果有 AI 预测且置信度高，自动勾选
    const pred = newImage.ai_prediction
    if (pred) {
      if (pred.aircraft_confidence >= 0.95) {
        useModelType.value = true
        form.value.typeId = pred.aircraft_class
        form.value.typeName = pred.aircraft_class
      }
      if (pred.airline_confidence >= 0.95) {
        useModelAirline.value = true
        form.value.airlineId = pred.airline_class
        form.value.airlineName = pred.airline_class
      }
      if (pred.registration && pred.registration_confidence >= 0.9) {
        useModelOcr.value = true
        form.value.registration = pred.registration
      }
      // 默认使用 AI 质量评估
      useModelQuality.value = true
      form.value.clarity = pred.clarity
      form.value.block = pred.block
    }
  }
}, { immediate: true })

// 使用模型预测切换事件
const onUseModelTypeChange = () => {
  if (useModelType.value && aiPrediction.value) {
    form.value.typeId = aiPrediction.value.aircraft_class
    form.value.typeName = aiPrediction.value.aircraft_class
  } else {
    form.value.typeId = ''
    form.value.typeName = ''
  }
}

const onUseModelAirlineChange = () => {
  if (useModelAirline.value && aiPrediction.value) {
    form.value.airlineId = aiPrediction.value.airline_class
    form.value.airlineName = aiPrediction.value.airline_class
  } else {
    form.value.airlineId = ''
    form.value.airlineName = ''
  }
}

const onUseModelOcrChange = () => {
  if (useModelOcr.value && aiPrediction.value) {
    form.value.registration = aiPrediction.value.registration
  } else {
    form.value.registration = ''
  }
}

const onUseModelQualityChange = () => {
  if (useModelQuality.value && aiPrediction.value) {
    form.value.clarity = aiPrediction.value.clarity
    form.value.block = aiPrediction.value.block
  } else {
    form.value.clarity = 0.8
    form.value.block = 0
  }
}

// 加载数据
const loadData = async () => {
  try {
    const [airlinesRes, typesRes] = await Promise.all([
      getAirlines(),
      getAircraftTypes()
    ])
    airlines.value = airlinesRes.data
    aircraftTypes.value = typesRes.data
  } catch (e) {
    console.error('加载数据失败:', e)
  }
}

// 航司选择变化
const onAirlineChange = () => {
  if (form.value.airlineId === '__new__') {
    showNewAirline.value = true
    form.value.airlineId = ''
  } else {
    const airline = airlines.value.find(a => a.code === form.value.airlineId)
    form.value.airlineName = airline?.name || ''
  }
}

// 机型选择变化
const onTypeChange = () => {
  if (form.value.typeId === '__new__') {
    showNewType.value = true
    form.value.typeId = ''
  } else {
    const type = aircraftTypes.value.find(t => t.code === form.value.typeId)
    form.value.typeName = type?.name || ''
  }
}

// 添加新航司
const addAirline = async () => {
  if (!newAirline.value.code || !newAirline.value.name) {
    error.value = '请填写航司代码和名称'
    return
  }

  try {
    await createAirline(newAirline.value)
    await loadData()
    form.value.airlineId = newAirline.value.code
    form.value.airlineName = newAirline.value.name
    cancelNewAirline()
  } catch (e) {
    error.value = e.response?.data?.error || '添加航司失败'
  }
}

const cancelNewAirline = () => {
  showNewAirline.value = false
  newAirline.value = { code: '', name: '' }
}

// 添加新机型
const addType = async () => {
  if (!newType.value.code || !newType.value.name) {
    error.value = '请填写机型代码和名称'
    return
  }

  try {
    await createAircraftType(newType.value)
    await loadData()
    form.value.typeId = newType.value.code
    form.value.typeName = newType.value.name
    cancelNewType()
  } catch (e) {
    error.value = e.response?.data?.error || '添加机型失败'
  }
}

const cancelNewType = () => {
  showNewType.value = false
  newType.value = { code: '', name: '' }
}

// 提交表单
const handleSubmit = async () => {
  if (!isValid.value) return

  loading.value = true
  error.value = ''

  try {
    const data = {
      airline_id: form.value.airlineId,
      airline_name: form.value.airlineName,
      type_id: form.value.typeId,
      type_name: form.value.typeName,
      registration: form.value.registration,
      clarity: form.value.clarity,
      block: form.value.block,
      registration_area: props.registrationArea,
      // AI 预测信息
      model_prediction_type: aiPrediction.value?.aircraft_class || null,
      model_prediction_airline: aiPrediction.value?.airline_class || null,
      model_confidence: aiPrediction.value?.aircraft_confidence || null,
      model_ocr_text: aiPrediction.value?.registration || null,
      // 是否使用模型预测
      use_model_type: useModelType.value,
      use_model_airline: useModelAirline.value,
      use_model_ocr: useModelOcr.value
    }
    emit('submit', data)
  } catch (e) {
    error.value = e.response?.data?.error || '保存失败'
  } finally {
    loading.value = false
  }
}

// 跳过
const handleSkip = () => {
  emit('skip')
}

// 标记为废图并跳过
const handleSkipAsInvalid = () => {
  emit('skipAsInvalid')
}

// 重置表单
const reset = () => {
  form.value = {
    airlineId: '',
    airlineName: '',
    typeId: '',
    typeName: '',
    registration: '',
    clarity: 0.8,
    block: 0
  }
  error.value = ''
  useModelType.value = false
  useModelAirline.value = false
  useModelOcr.value = false
  useModelQuality.value = false
}

// 监听初始数据
watch(() => props.initialData, (data) => {
  if (data) {
    form.value = {
      airlineId: data.airline_id || '',
      airlineName: data.airline_name || '',
      typeId: data.type_id || '',
      typeName: data.type_name || '',
      registration: data.registration || '',
      clarity: data.clarity ?? 0.8,
      block: data.block ?? 0
    }
  }
}, { immediate: true })

// 暴露方法
defineExpose({ reset })

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.label-form {
  padding: 20px;
  background: #252525;
  border-radius: 8px;
}

.label-form h3 {
  margin: 0 0 20px 0;
  color: #fff;
  font-size: 18px;
}

/* AI 预测横幅 */
.ai-prediction-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #1a3a5c 0%, #2d1a4a 100%);
  border-radius: 6px;
  border: 1px solid #3a5a8c;
}

.ai-badge {
  padding: 4px 8px;
  background: #4a90d9;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: #fff;
}

.new-class-badge {
  padding: 4px 8px;
  background: #ff9800;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: #000;
}

/* 模型预测卡片 */
.model-prediction {
  margin-bottom: 16px;
}

.model-prediction > label {
  display: block;
  margin-bottom: 6px;
  color: #aaa;
  font-size: 14px;
}

.prediction-card {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 6px;
  padding: 12px;
}

.prediction-card .top1,
.prediction-card .ocr-result {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.prediction-card .class-name,
.prediction-card .text {
  font-size: 16px;
  font-weight: bold;
  color: #fff;
}

.prediction-card .confidence {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: bold;
}

.prediction-card .confidence.high {
  background: #2d5a2d;
  color: #8fdf8f;
}

.prediction-card .confidence.medium {
  background: #5a5a2d;
  color: #dfdf8f;
}

.prediction-card .confidence.low {
  background: #5a2d2d;
  color: #df8f8f;
}

.prediction-card .warning {
  padding: 6px 10px;
  background: #3a2a1a;
  border-radius: 4px;
  color: #ff9800;
  font-size: 12px;
  margin-bottom: 8px;
}

.prediction-card .checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #aaa;
  font-size: 13px;
}

.prediction-card .checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

/* 质量评估 */
.quality-prediction .quality-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  color: #aaa;
  font-size: 14px;
}

.quality-prediction .quality-value {
  font-weight: bold;
  color: #4a90d9;
}

.form-group {
  margin-bottom: 16px;
}

.form-group.disabled {
  opacity: 0.5;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #aaa;
  font-size: 14px;
}

.form-group select,
.form-group input[type="text"],
.form-group input:not([type="range"]) {
  width: 100%;
  padding: 10px;
  border: 1px solid #444;
  border-radius: 4px;
  background: #1a1a1a;
  color: #fff;
  font-size: 14px;
}

.form-group select:focus,
.form-group input:focus {
  outline: none;
  border-color: #4a90d9;
}

.form-group input[type="range"] {
  width: 100%;
  margin-top: 8px;
}

.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.new-item-form {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.new-item-form input {
  flex: 1;
  padding: 8px;
}

.new-item-form button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.new-item-form button:first-of-type {
  background: #4a90d9;
  color: #fff;
}

.new-item-form button:last-of-type {
  background: #444;
  color: #fff;
}

.area-info .area-display {
  background: #1a1a1a;
  padding: 12px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}

.area-info .area-display div {
  color: #888;
}

.area-info .area-display div.valid {
  color: #4caf50;
}

.error-message {
  margin-top: 16px;
  padding: 12px;
  background: #442222;
  border: 1px solid #663333;
  border-radius: 4px;
  color: #ff6666;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 24px;
}

.submit-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 4px;
  background: #4a90d9;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #5a9fe9;
}

.submit-btn:disabled {
  background: #444;
  cursor: not-allowed;
}

.skip-btn {
  padding: 12px 16px;
  border: 1px solid #666;
  border-radius: 4px;
  background: transparent;
  color: #aaa;
  cursor: pointer;
  transition: all 0.2s;
}

.skip-btn:hover {
  border-color: #888;
  color: #fff;
}

.skip-invalid-btn {
  padding: 12px 16px;
  border: 1px solid #aa3333;
  border-radius: 4px;
  background: transparent;
  color: #ff6666;
  cursor: pointer;
  transition: all 0.2s;
}

.skip-invalid-btn:hover {
  background: #aa3333;
  color: #fff;
}
</style>
