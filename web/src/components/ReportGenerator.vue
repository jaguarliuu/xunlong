<template>
  <div class="report-generator">
    <div class="card">
      <h2>📊 报告生成器</h2>
      <p class="description">基于主题生成专业的研究报告，支持多种格式导出</p>

      <form @submit.prevent="generateReport">
        <div class="form-group">
          <label for="query">报告主题 *</label>
          <input
            id="query"
            v-model="formData.query"
            type="text"
            placeholder="例如：2024年人工智能发展趋势"
            required
          />
        </div>

        <div class="form-group">
          <label for="description">详细描述</label>
          <textarea
            id="description"
            v-model="formData.description"
            placeholder="请详细描述报告的内容要求、研究方向等（可选）"
          ></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="report-type">报告类型</label>
            <select id="report-type" v-model="formData.report_type">
              <option value="comprehensive">综合报告</option>
              <option value="daily">每日报告</option>
              <option value="analysis">分析报告</option>
              <option value="research">研究报告</option>
            </select>
          </div>

          <div class="form-group">
            <label for="search-depth">搜索深度</label>
            <select id="search-depth" v-model="formData.search_depth">
              <option value="surface">表面</option>
              <option value="medium">中等</option>
              <option value="deep">深度</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="html-template">HTML模板</label>
            <select id="html-template" v-model="formData.html_template">
              <option value="academic">学术风格</option>
              <option value="technical">技术风格</option>
            </select>
          </div>

          <div class="form-group">
            <label for="html-theme">主题</label>
            <select id="html-theme" v-model="formData.html_theme">
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
          <span v-if="!loading">🚀 生成报告</span>
          <span v-else>⏳ 生成中...</span>
        </button>
      </form>

      <!-- 生成进度 -->
      <div v-if="loading" class="progress-section">
        <div class="progress-bar">
          <div class="progress-bar-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <p class="progress-text">{{ statusText }}</p>
      </div>

      <!-- 结果展示 -->
      <div v-if="result" class="result-section">
        <div class="alert alert-success">
          ✅ 报告生成成功！任务ID: {{ taskId }}
        </div>

        <div class="result-actions">
          <button class="btn btn-primary" @click="downloadFile('html')">
            📥 下载HTML
          </button>
          <button class="btn btn-primary" @click="downloadFile('md')">
            📥 下载Markdown
          </button>
          <button class="btn btn-secondary" @click="viewResult">
            👁️ 预览结果
          </button>
        </div>

        <div v-if="showPreview" class="preview-section">
          <h3>报告预览</h3>
          <div class="preview-content" v-html="result.content"></div>
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
import { ref } from 'vue'
import { api } from '../api'

const formData = ref({
  query: '',
  description: '',
  report_type: 'comprehensive',
  search_depth: 'deep',
  max_results: 20,
  output_format: 'html',
  html_template: 'academic',
  html_theme: 'light'
})

const loading = ref(false)
const progress = ref(0)
const statusText = ref('')
const taskId = ref(null)
const result = ref(null)
const error = ref(null)
const showPreview = ref(false)

let pollInterval = null

const emit = defineEmits(['view-task'])

const generateReport = async () => {
  loading.value = true
  error.value = null
  result.value = null
  progress.value = 0
  statusText.value = '正在创建任务...'

  try {
    // 创建任务
    const response = await api.createReport(formData.value)
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

      // 更新进度
      if (status.progress !== undefined) {
        progress.value = status.progress
      }

      if (status.status_text) {
        statusText.value = status.status_text
      }

      // 检查任务状态
      if (status.status === 'completed') {
        clearInterval(pollInterval)
        // 获取任务结果
        const taskResult = await api.getTaskResult(taskId.value)
        result.value = taskResult
        loading.value = false
        progress.value = 100
        statusText.value = '报告生成完成！'
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
  }, 2000) // 每2秒轮询一次
}

const downloadFile = (fileType) => {
  api.downloadTaskFile(taskId.value, fileType)
}

const viewResult = () => {
  showPreview.value = !showPreview.value
}

// 清理定时器
const cleanup = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
}

// 组件卸载时清理
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  cleanup()
})
</script>

<style scoped>
.report-generator {
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

.result-section {
  margin-top: 30px;
}

.result-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;
}

.preview-section {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  max-height: 500px;
  overflow-y: auto;
}

.preview-section h3 {
  margin-bottom: 15px;
  color: #333;
}

.preview-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  line-height: 1.6;
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
}
</style>
