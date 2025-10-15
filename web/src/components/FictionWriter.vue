<template>
  <div class="fiction-writer">
    <div class="card">
      <h2>📖 小说创作器</h2>
      <p class="description">基于AI生成创意小说，支持多种类型和风格</p>

      <form @submit.prevent="generateFiction">
        <div class="form-group">
          <label for="query">小说主题/提示 *</label>
          <textarea
            id="query"
            v-model="formData.query"
            placeholder="例如：一个关于时间旅行者的悬疑故事，主角发现改变过去会导致意想不到的后果..."
            rows="4"
            required
          ></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="genre">小说体裁</label>
            <select id="genre" v-model="formData.genre">
              <option value="mystery">悬疑</option>
              <option value="scifi">科幻</option>
              <option value="fantasy">奇幻</option>
              <option value="horror">恐怖</option>
              <option value="romance">言情</option>
              <option value="wuxia">武侠</option>
            </select>
          </div>

          <div class="form-group">
            <label for="length">篇幅长度</label>
            <select id="length" v-model="formData.length">
              <option value="short">短篇</option>
              <option value="medium">中篇</option>
              <option value="long">长篇</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="viewpoint">叙事视角</label>
            <select id="viewpoint" v-model="formData.viewpoint">
              <option value="first">第一人称</option>
              <option value="third">第三人称</option>
              <option value="omniscient">全知视角</option>
            </select>
          </div>

          <div class="form-group">
            <label for="html-theme">主题</label>
            <select id="html-theme" v-model="formData.html_theme">
              <option value="sepia">复古棕</option>
              <option value="light">浅色</option>
              <option value="dark">深色</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          class="btn btn-primary"
          :disabled="loading || !formData.query"
        >
          <span v-if="!loading">✍️ 开始创作</span>
          <span v-else>⏳ 创作中...</span>
        </button>
      </form>

      <!-- 创作进度 -->
      <div v-if="loading" class="progress-section">
        <div class="progress-bar">
          <div class="progress-bar-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <p class="progress-text">{{ statusText }}</p>
        <p v-if="currentChapter" class="chapter-info">
          正在创作第 {{ currentChapter }} 章
        </p>
      </div>

      <!-- 结果展示 -->
      <div v-if="result" class="result-section">
        <div class="alert alert-success">
          ✅ 小说创作成功！任务ID: {{ taskId }}
        </div>

        <div class="fiction-info">
          <h3>{{ result.title || '小说作品' }}</h3>
          <p class="meta">
            <span>体裁: {{ genreText }}</span>
            <span>篇幅: {{ lengthText }}</span>
            <span>视角: {{ viewpointText }}</span>
          </p>
        </div>

        <div class="result-actions">
          <button class="btn btn-primary" @click="downloadFile('html')">
            📥 下载HTML
          </button>
          <button class="btn btn-primary" @click="downloadFile('md')">
            📥 下载Markdown
          </button>
          <button class="btn btn-secondary" @click="viewResult">
            👁️ {{ showPreview ? '隐藏预览' : '查看预览' }}
          </button>
        </div>

        <div v-if="showPreview" class="preview-section">
          <div class="chapter-list">
            <div
              v-for="(chapter, index) in result.chapters"
              :key="index"
              class="chapter-item"
              @click="selectChapter(index)"
            >
              <h4 :class="{ active: selectedChapter === index }">
                第{{ index + 1 }}章: {{ chapter.title }}
              </h4>
            </div>
          </div>
          <div v-if="selectedChapter !== null" class="chapter-content">
            <h3>{{ result.chapters[selectedChapter].title }}</h3>
            <div v-html="result.chapters[selectedChapter].content"></div>
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
  genre: 'mystery',
  length: 'short',
  viewpoint: 'first',
  constraints: [],
  output_format: 'html',
  html_template: 'novel',
  html_theme: 'sepia'
})

const loading = ref(false)
const progress = ref(0)
const statusText = ref('')
const currentChapter = ref(null)
const taskId = ref(null)
const result = ref(null)
const error = ref(null)
const showPreview = ref(false)
const selectedChapter = ref(null)

let pollInterval = null

const genreMap = {
  mystery: '悬疑',
  scifi: '科幻',
  fantasy: '奇幻',
  horror: '恐怖',
  romance: '言情',
  wuxia: '武侠'
}

const lengthMap = {
  short: '短篇',
  medium: '中篇',
  long: '长篇'
}

const viewpointMap = {
  first: '第一人称',
  third: '第三人称',
  omniscient: '全知视角'
}

const genreText = computed(() => genreMap[formData.value.genre])
const lengthText = computed(() => lengthMap[formData.value.length])
const viewpointText = computed(() => viewpointMap[formData.value.viewpoint])

const emit = defineEmits(['view-task'])

const generateFiction = async () => {
  loading.value = true
  error.value = null
  result.value = null
  progress.value = 0
  currentChapter.value = null
  statusText.value = '正在创建任务...'

  try {
    const response = await api.createFiction(formData.value)
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

      if (status.current_chapter) {
        currentChapter.value = status.current_chapter
      }

      if (status.status === 'completed') {
        clearInterval(pollInterval)
        const taskResult = await api.getTaskResult(taskId.value)
        result.value = taskResult
        loading.value = false
        progress.value = 100
        statusText.value = '小说创作完成！'
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
  if (showPreview.value && selectedChapter.value === null && result.value?.chapters?.length) {
    selectedChapter.value = 0
  }
}

const selectChapter = (index) => {
  selectedChapter.value = index
}

import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<style scoped>
.fiction-writer {
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

.chapter-info {
  text-align: center;
  color: #764ba2;
  font-weight: 500;
  margin-top: 5px;
}

.result-section {
  margin-top: 30px;
}

.fiction-info {
  margin: 20px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.fiction-info h3 {
  color: #333;
  margin-bottom: 10px;
}

.fiction-info .meta {
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
  grid-template-columns: 250px 1fr;
  gap: 20px;
}

.chapter-list {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  max-height: 500px;
  overflow-y: auto;
}

.chapter-item {
  cursor: pointer;
  margin-bottom: 10px;
}

.chapter-item h4 {
  padding: 10px;
  border-radius: 6px;
  font-size: 14px;
  color: #555;
  transition: all 0.3s;
}

.chapter-item h4:hover {
  background: white;
  color: #667eea;
}

.chapter-item h4.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.chapter-content {
  background: white;
  padding: 25px;
  border-radius: 8px;
  max-height: 500px;
  overflow-y: auto;
  line-height: 1.8;
}

.chapter-content h3 {
  margin-bottom: 20px;
  color: #333;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
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

  .chapter-list {
    max-height: 200px;
  }
}
</style>
