<template>
  <div class="ppt-creator">
    <div class="card">
      <h2>🎬 PPT生成器</h2>
      <p class="description">基于主题自动生成专业的PPT演示文稿</p>

      <form @submit.prevent="generatePPT">
        <div class="form-group">
          <label for="query">PPT主题 *</label>
          <textarea
            id="query"
            v-model="formData.query"
            placeholder="例如：人工智能在教育领域的应用 - 包括AI教学助手、个性化学习、自动评分系统等方面"
            rows="4"
            required
          ></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="slides">幻灯片数量</label>
            <input
              id="slides"
              v-model.number="formData.slides"
              type="number"
              min="5"
              max="50"
            />
          </div>

          <div class="form-group">
            <label for="style">演示风格</label>
            <select id="style" v-model="formData.style">
              <option value="business">商务风格</option>
              <option value="creative">创意设计</option>
              <option value="minimal">简约风格</option>
              <option value="educational">教育风格</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="theme">主题配色</label>
          <select id="theme" v-model="formData.theme">
            <option value="corporate-blue">企业蓝</option>
            <option value="tech-dark">科技黑</option>
            <option value="nature-green">自然绿</option>
            <option value="elegant-purple">优雅紫</option>
            <option value="warm-orange">温暖橙</option>
          </select>
        </div>

        <button
          type="submit"
          class="btn btn-primary"
          :disabled="loading || !formData.query"
        >
          <span v-if="!loading">🚀 生成PPT</span>
          <span v-else>⏳ 生成中...</span>
        </button>
      </form>

      <!-- 生成进度 -->
      <div v-if="loading" class="progress-section">
        <div class="progress-bar">
          <div class="progress-bar-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <p class="progress-text">{{ statusText }}</p>
        <p v-if="currentSlide" class="slide-info">
          正在生成第 {{ currentSlide }} / {{ formData.num_slides }} 页
        </p>
      </div>

      <!-- 结果展示 -->
      <div v-if="result" class="result-section">
        <div class="alert alert-success">
          ✅ PPT生成成功！任务ID: {{ taskId }}
        </div>

        <div class="ppt-info">
          <h3>{{ result.title || 'PPT演示文稿' }}</h3>
          <p class="meta">
            <span>📊 {{ formData.slides }} 页</span>
            <span>🎨 {{ styleText }}</span>
            <span>🎨 {{ themeText }}</span>
          </p>
        </div>

        <div class="result-actions">
          <button class="btn btn-primary" @click="downloadFile('pptx')">
            📥 下载PPTX
          </button>
          <button class="btn btn-primary" @click="downloadFile('pdf')">
            📥 下载PDF
          </button>
          <button class="btn btn-secondary" @click="viewResult">
            👁️ {{ showPreview ? '隐藏预览' : '查看预览' }}
          </button>
        </div>

        <div v-if="showPreview && result.slides" class="preview-section">
          <div class="slide-thumbnails">
            <div
              v-for="(slide, index) in result.slides"
              :key="index"
              class="thumbnail-item"
              :class="{ active: selectedSlide === index }"
              @click="selectSlide(index)"
            >
              <div class="thumbnail-number">{{ index + 1 }}</div>
              <div class="thumbnail-title">{{ slide.title }}</div>
            </div>
          </div>
          <div v-if="selectedSlide !== null" class="slide-preview">
            <div class="slide-content">
              <h2>{{ result.slides[selectedSlide].title }}</h2>
              <div v-html="result.slides[selectedSlide].content"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="alert alert-error">
        ❌ {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { api } from '../api'

const formData = ref({
  query: '',
  slides: 15,
  style: 'business',
  theme: 'corporate-blue'
})

const loading = ref(false)
const progress = ref(0)
const statusText = ref('')
const currentSlide = ref(null)
const taskId = ref(null)
const result = ref(null)
const error = ref(null)
const showPreview = ref(false)
const selectedSlide = ref(null)

let pollInterval = null

const styleMap = {
  business: '商务风格',
  creative: '创意设计',
  minimal: '简约风格',
  educational: '教育风格'
}

const themeMap = {
  'corporate-blue': '企业蓝',
  'tech-dark': '科技黑',
  'nature-green': '自然绿',
  'elegant-purple': '优雅紫',
  'warm-orange': '温暖橙'
}

const styleText = computed(() => styleMap[formData.value.style])
const themeText = computed(() => themeMap[formData.value.theme])

const emit = defineEmits(['view-task'])

const generatePPT = async () => {
  loading.value = true
  error.value = null
  result.value = null
  progress.value = 0
  currentSlide.value = null
  statusText.value = '正在创建任务...'

  try {
    const response = await api.createPPT(formData.value)
    taskId.value = response.task_id

    // 跳转到任务详情页面
    emit('view-task', taskId.value)

    loading.value = false
  } catch (err) {
    error.value = err.message
    loading.value = false
  }
}

const startPolling = () => {
  pollInterval = setInterval(async () => {
    try {
      const status = await api.getTaskStatus(taskId.value)

      if (status.progress !== undefined) {
        progress.value = status.progress
      }

      if (status.status_text) {
        statusText.value = status.status_text
      }

      if (status.current_step) {
        const match = status.current_step.match(/(\d+)/)
        if (match) {
          currentSlide.value = parseInt(match[1])
        }
      }

      if (status.status === 'completed') {
        clearInterval(pollInterval)
        const taskResult = await api.getTaskResult(taskId.value)
        result.value = taskResult
        loading.value = false
        progress.value = 100
        statusText.value = 'PPT生成完成！'
      } else if (status.status === 'failed') {
        clearInterval(pollInterval)
        error.value = status.error || '任务执行失败'
        loading.value = false
      }
    } catch (err) {
      clearInterval(pollInterval)
      error.value = err.message
      loading.value = false
    }
  }, 5000)
}

const downloadFile = (fileType) => {
  api.downloadTaskFile(taskId.value, fileType)
}

const viewResult = () => {
  showPreview.value = !showPreview.value
  if (showPreview.value && selectedSlide.value === null && result.value?.slides?.length) {
    selectedSlide.value = 0
  }
}

const selectSlide = (index) => {
  selectedSlide.value = index
}

import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<style scoped>
.ppt-creator {
  max-width: 800px;
  margin: 0 auto;
}

.description {
  color: #666;
  margin-bottom: 24px;
  font-size: 14px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group label[type="checkbox"] {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.form-group input[type="checkbox"] {
  width: auto;
  cursor: pointer;
}

.progress-section {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.progress-text {
  text-align: center;
  color: #667eea;
  font-weight: 500;
  margin-top: 10px;
}

.slide-info {
  text-align: center;
  color: #764ba2;
  font-weight: 500;
  margin-top: 5px;
}

.result-section {
  margin-top: 30px;
}

.ppt-info {
  margin: 20px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.ppt-info h3 {
  color: #333;
  margin-bottom: 10px;
}

.ppt-info .meta {
  display: flex;
  gap: 20px;
  color: #666;
  font-size: 14px;
}

.result-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.preview-section {
  margin-top: 20px;
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 20px;
}

.slide-thumbnails {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  max-height: 600px;
  overflow-y: auto;
}

.thumbnail-item {
  background: white;
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.thumbnail-item:hover {
  border-color: #667eea;
  transform: translateX(5px);
}

.thumbnail-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
}

.thumbnail-number {
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 5px;
}

.thumbnail-title {
  font-size: 12px;
  line-height: 1.4;
}

.slide-preview {
  background: white;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  min-height: 400px;
}

.slide-content h2 {
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 3px solid #667eea;
}

.slide-content {
  line-height: 1.8;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .result-actions {
    flex-direction: column;
  }

  .result-actions button {
    width: 100%;
  }

  .preview-section {
    grid-template-columns: 1fr;
  }

  .slide-thumbnails {
    max-height: 200px;
  }
}
</style>
