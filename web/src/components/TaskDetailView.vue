<template>
  <div class="task-detail-view">
    <!-- 顶部信息栏 -->
    <div class="task-header">
      <div class="task-header-left">
        <button class="back-btn" @click="$emit('back')">
          ← 返回
        </button>
        <div class="task-info">
          <h2>{{ taskInfo?.query || '加载中...' }}</h2>
          <div class="task-meta">
            <span class="task-type">{{ getTaskTypeName(taskInfo?.type) }}</span>
            <span class="task-status" :class="'status-' + taskInfo?.status">
              {{ getStatusText(taskInfo?.status) }}
            </span>
            <span class="task-id">ID: {{ taskId }}</span>
          </div>
        </div>
      </div>
      <div class="task-header-right">
        <button v-if="taskInfo?.status === 'completed'" class="btn btn-primary" @click="downloadFile">
          📥 下载结果
        </button>
        <button v-if="taskInfo?.status === 'running'" class="btn btn-secondary" @click="cancelTask">
          🚫 取消任务
        </button>
      </div>
    </div>

    <!-- 进度条 -->
    <div v-if="taskInfo?.status === 'running'" class="progress-section">
      <div class="progress-bar">
        <div class="progress-bar-fill" :style="{ width: taskInfo.progress + '%' }"></div>
      </div>
      <p class="progress-text">{{ taskInfo.progress }}% - {{ taskInfo.current_step }}</p>
    </div>

    <!-- 左右分栏 -->
    <div class="task-content">
      <!-- 左侧：日志面板 -->
      <div class="logs-panel">
        <div class="panel-header">
          <h3>📋 执行日志</h3>
          <button class="auto-scroll-btn" :class="{ active: autoScroll }" @click="toggleAutoScroll">
            {{ autoScroll ? '🔒 自动滚动' : '🔓 手动' }}
          </button>
        </div>
        <div class="logs-content" ref="logsContainer">
          <div v-for="(log, index) in logs" :key="index" class="log-entry" :class="'log-' + log.level">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-level">{{ log.level }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
          <div v-if="!logs.length" class="empty-logs">
            <p>暂无日志...</p>
          </div>
        </div>
      </div>

      <!-- 右侧：内容预览 -->
      <div class="preview-panel">
        <div class="panel-header">
          <h3>👁️ 内容预览</h3>
          <div class="preview-actions">
            <button
              v-for="format in ['rendered', 'markdown', 'raw']"
              :key="format"
              class="format-btn"
              :class="{ active: previewFormat === format }"
              @click="previewFormat = format"
            >
              {{ formatNames[format] }}
            </button>
          </div>
        </div>
        <div class="preview-content">
          <div v-if="taskInfo?.status === 'completed'" class="content-view">
            <iframe
              v-if="previewFormat === 'rendered'"
              class="rendered-view"
              :srcdoc="renderedContent"
              style="width:100%;height:100%;border:none;min-height:400px;display:block;"
              ref="renderedIframe"
              @load="e => e.target.style.height = e.target.contentDocument?.body?.scrollHeight + 'px'"
            ></iframe>
            <iframe
              v-else-if="previewFormat === 'markdown'" class="markdown-view"
              :srcdoc="`<body style='margin:0;padding:16px;font-family:monospace;background:#f8f9fa;min-height:400px;'>${markdownContent.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>')}</body>`"
              style="width:100%;height:auto;border:none;min-height:400px;display:block;"
              ref="markdownIframe"
              @load="e => e.target.style.height = e.target.contentDocument?.body?.scrollHeight + 'px'"
            ></iframe>
            <div v-else class="raw-view">
              <pre>{{ JSON.stringify(taskInfo.result, null, 2) }}</pre>
            </div>
          </div>
          <div v-else-if="taskInfo?.status === 'running'" class="loading-view">
            <div class="spinner"></div>
            <p>生成中，请稍候...</p>
          </div>
          <div v-else-if="taskInfo?.status === 'failed'" class="error-view">
            <div class="error-icon">❌</div>
            <p>任务执行失败</p>
            <p class="error-message">{{ taskInfo.error }}</p>
          </div>
          <div v-else class="empty-view">
            <p>等待生成...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { api } from '../api'

const props = defineProps({
  taskId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['back'])

const taskInfo = ref(null)
const logs = ref([])
const autoScroll = ref(true)
const previewFormat = ref('rendered')
const renderedContent = ref('')
const markdownContent = ref('')
const logsContainer = ref(null)

let pollInterval = null

const formatNames = {
  rendered: '渲染视图',
  markdown: 'Markdown',
  raw: '原始数据'
}

const taskTypeMap = {
  report: '报告生成',
  fiction: '小说创作',
  ppt: 'PPT生成'
}

const statusMap = {
  pending: '待处理',
  running: '执行中',
  completed: '已完成',
  failed: '失败'
}

const getTaskTypeName = (type) => taskTypeMap[type] || type
const getStatusText = (status) => statusMap[status] || status

const loadTaskInfo = async () => {
  try {
    const data = await api.getTaskStatus(props.taskId)
    taskInfo.value = data

    // 添加日志
    if (data.current_step) {
      addLog('info', data.current_step)
    }

    // 如果任务完成，加载结果
    if (data.status === 'completed' && !renderedContent.value) {
      await loadTaskResult()
    }

    // 如果任务失败，添加错误日志
    if (data.status === 'failed' && data.error) {
      addLog('error', data.error)
    }
  } catch (err) {
    addLog('error', `加载任务信息失败: ${err.message}`)
  }
}

const loadTaskResult = async () => {
  try {
    const result = await api.getTaskResult(props.taskId)
    taskInfo.value.result = result

    // 尝试提取内容
    if (result.content) {
      renderedContent.value = result.content
    } else if (result.html_content) {
      renderedContent.value = result.html_content
    }

    if (result.markdown) {
      markdownContent.value = result.markdown
    }

    addLog('success', '任务结果加载完成')
  } catch (err) {
    addLog('error', `加载结果失败: ${err.message}`)
  }
}

const addLog = (level, message) => {
  const now = new Date()
  const time = now.toLocaleTimeString('zh-CN')

  // 避免重复日志
  const lastLog = logs.value[logs.value.length - 1]
  if (lastLog && lastLog.message === message) {
    return
  }

  logs.value.push({
    time,
    level,
    message
  })

  // 自动滚动
  if (autoScroll.value) {
    nextTick(() => {
      if (logsContainer.value) {
        logsContainer.value.scrollTop = logsContainer.value.scrollHeight
      }
    })
  }

  // 限制日志数量
  if (logs.value.length > 100) {
    logs.value.shift()
  }
}

const toggleAutoScroll = () => {
  autoScroll.value = !autoScroll.value
}

const downloadFile = () => {
  const fileType = taskInfo.value.type === 'ppt' ? 'pptx' : 'html'
  api.downloadTaskFile(props.taskId, fileType)
  addLog('info', `开始下载文件: ${fileType}`)
}

const cancelTask = async () => {
  if (!confirm('确定要取消这个任务吗？')) return

  try {
    await api.cancelTask(props.taskId)
    addLog('warning', '任务已取消')
    await loadTaskInfo()
  } catch (err) {
    addLog('error', `取消任务失败: ${err.message}`)
  }
}

const startPolling = () => {
  pollInterval = setInterval(async () => {
    await loadTaskInfo()

    // 如果任务结束，停止轮询
    if (taskInfo.value && ['completed', 'failed', 'cancelled'].includes(taskInfo.value.status)) {
      stopPolling()
    }
  }, 5000)
}

const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

onMounted(() => {
  addLog('info', '开始加载任务信息...')
  loadTaskInfo()
  startPolling()
})

onBeforeUnmount(() => {
  stopPolling()
})

// 监听任务状态变化
watch(() => taskInfo.value?.status, (newStatus, oldStatus) => {
  if (newStatus && newStatus !== oldStatus) {
    addLog('info', `任务状态: ${getStatusText(oldStatus)} → ${getStatusText(newStatus)}`)
  }
})
</script>

<style scoped>
.task-detail-view {
  max-width: 1600px;
  margin: 0 auto;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: white;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.task-header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-btn {
  padding: 8px 16px;
  border: none;
  background: #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.back-btn:hover {
  background: #e0e0e0;
}

.task-info h2 {
  font-size: 20px;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.task-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
}

.task-type {
  padding: 4px 12px;
  background: #f0f0f0;
  border-radius: 12px;
  color: #666;
}

.task-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 500;
}

.task-status.status-pending {
  background: #fff3cd;
  color: #856404;
}

.task-status.status-running {
  background: #cfe2ff;
  color: #084298;
}

.task-status.status-completed {
  background: #d1e7dd;
  color: #0f5132;
}

.task-status.status-failed {
  background: #f8d7da;
  color: #842029;
}

.task-id {
  color: #999;
  font-family: monospace;
  font-size: 12px;
}

.task-header-right {
  display: flex;
  gap: 10px;
}

.progress-section {
  background: white;
  padding: 20px 24px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.progress-text {
  text-align: center;
  color: #667eea;
  font-weight: 500;
  margin-top: 12px;
  font-size: 14px;
}

.task-content {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 20px;
  height: calc(100vh - 400px);
  min-height: 500px;
}

.logs-panel,
.preview-panel {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fafafa;
}

.panel-header h3 {
  font-size: 16px;
  color: #1a1a1a;
  font-weight: 600;
}

.auto-scroll-btn {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}

.auto-scroll-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.logs-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  background: #1a1a1a;
  color: #e0e0e0;
}

.log-entry {
  margin-bottom: 8px;
  display: flex;
  gap: 12px;
}

.log-time {
  color: #666;
  min-width: 80px;
}

.log-level {
  min-width: 50px;
  font-weight: 600;
}

.log-info .log-level {
  color: #4a9eff;
}

.log-success .log-level {
  color: #52c41a;
}

.log-warning .log-level {
  color: #faad14;
}

.log-error .log-level {
  color: #f5222d;
}

.log-message {
  flex: 1;
  word-break: break-word;
}

.empty-logs {
  text-align: center;
  padding: 40px;
  color: #666;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.format-btn {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}

.format-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.content-view {
  min-height: 100%;
}

.rendered-view {
  line-height: 1.8;
}

.markdown-view,
.raw-view {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.markdown-view pre,
.raw-view pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.loading-view,
.error-view,
.empty-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-message {
  color: #f5222d;
  margin-top: 8px;
  font-size: 14px;
}

@media (max-width: 1024px) {
  .task-content {
    grid-template-columns: 1fr;
    height: auto;
  }

  .logs-panel {
    height: 300px;
  }

  .preview-panel {
    height: 400px;
  }
}
</style>
