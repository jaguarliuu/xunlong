<template>
  <div class="task-monitor">
    <div class="card">
      <h2>📋 任务监控</h2>
      <p class="description">查看和管理所有任务的执行状态</p>

      <div class="toolbar">
        <button class="btn btn-primary" @click="refreshTasks">
          🔄 刷新
        </button>
        <div class="filter-group">
          <label for="status-filter">状态筛选:</label>
          <select id="status-filter" v-model="filterStatus">
            <option value="">全部</option>
            <option value="pending">待处理</option>
            <option value="running">运行中</option>
            <option value="completed">已完成</option>
            <option value="failed">失败</option>
          </select>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading && !tasks.length" class="loading-section">
        <div class="spinner"></div>
        <p>加载任务列表...</p>
      </div>

      <!-- 任务列表 -->
      <div v-else-if="filteredTasks.length" class="tasks-list">
        <div
          v-for="task in filteredTasks"
          :key="task.task_id"
          class="task-item"
          :class="'status-' + task.status"
        >
          <div class="task-header">
            <div class="task-info">
              <span class="task-type">{{ getTaskTypeIcon(task.type) }} {{ getTaskTypeName(task.type) }}</span>
              <span class="task-id">ID: {{ task.task_id }}</span>
            </div>
            <div class="task-status">
              <span :class="'status-badge status-' + task.status">
                {{ getStatusText(task.status) }}
              </span>
            </div>
          </div>

          <div class="task-body">
            <h3>{{ task.title || task.query || '任务' }}</h3>
            <p class="task-meta">
              <span>创建时间: {{ formatTime(task.created_at) }}</span>
              <span v-if="task.completed_at">完成时间: {{ formatTime(task.completed_at) }}</span>
            </p>

            <!-- 进度条 -->
            <div v-if="task.status === 'running'" class="task-progress">
              <div class="progress-bar">
                <div class="progress-bar-fill" :style="{ width: task.progress + '%' }"></div>
              </div>
              <p class="progress-info">
                {{ task.status_text || '处理中...' }} ({{ task.progress }}%)
              </p>
            </div>

            <!-- 错误信息 -->
            <div v-if="task.status === 'failed' && task.error" class="task-error">
              ❌ {{ task.error }}
            </div>
          </div>

          <div class="task-actions">
            <button
              class="btn btn-secondary"
              @click="viewTaskResult(task.task_id)"
            >
              👁️ 查看详情
            </button>
            <button
              v-if="task.status === 'completed'"
              class="btn btn-primary"
              @click="downloadTask(task.task_id)"
            >
              📥 下载
            </button>
            <button
              v-if="task.status === 'running' || task.status === 'pending'"
              class="btn btn-secondary"
              @click="cancelTask(task.task_id)"
            >
              🚫 取消
            </button>
            <button
              class="btn btn-secondary"
              @click="deleteTask(task.task_id)"
            >
              🗑️ 删除
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <p>📭 暂无任务</p>
        <p class="empty-hint">开始创建报告、小说或PPT任务吧！</p>
      </div>

      <!-- 任务详情弹窗 -->
      <div v-if="selectedTask" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>任务详情</h3>
            <button class="close-btn" @click="closeModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="detail-section">
              <h4>基本信息</h4>
              <p><strong>任务ID:</strong> {{ selectedTask.task_id }}</p>
              <p><strong>类型:</strong> {{ getTaskTypeName(selectedTask.type) }}</p>
              <p><strong>状态:</strong> {{ getStatusText(selectedTask.status) }}</p>
              <p><strong>标题:</strong> {{ selectedTask.title || selectedTask.query || '任务' }}</p>
            </div>

            <div v-if="selectedTask.result" class="detail-section">
              <h4>结果预览</h4>
              <div class="result-preview" v-html="selectedTask.result.content"></div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">关闭</button>
            <button
              v-if="selectedTask.status === 'completed'"
              class="btn btn-primary"
              @click="downloadTask(selectedTask.task_id)"
            >
              📥 下载
            </button>
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../api'

const tasks = ref([])
const loading = ref(false)
const error = ref(null)
const filterStatus = ref('')

let refreshInterval = null

const taskTypeMap = {
  report: { name: '报告生成', icon: '📊' },
  fiction: { name: '小说创作', icon: '📖' },
  ppt: { name: 'PPT生成', icon: '🎬' }
}

const statusMap = {
  pending: '待处理',
  running: '运行中',
  completed: '已完成',
  failed: '失败'
}

const filteredTasks = computed(() => {
  if (!filterStatus.value) return tasks.value
  return tasks.value.filter(task => task.status === filterStatus.value)
})

const getTaskTypeName = (type) => {
  return taskTypeMap[type]?.name || type
}

const getTaskTypeIcon = (type) => {
  return taskTypeMap[type]?.icon || '📄'
}

const getStatusText = (status) => {
  return statusMap[status] || status
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

const loadTasks = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await api.listTasks()
    tasks.value = response.tasks || []
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const refreshTasks = () => {
  loadTasks()
}

const emit = defineEmits(['view-task'])

const viewTaskResult = (taskId) => {
  emit('view-task', taskId)
}

const downloadTask = (taskId) => {
  const task = tasks.value.find(t => t.task_id === taskId)
  if (!task) return

  let fileType = 'html'
  if (task.type === 'ppt') {
    fileType = 'pptx'
  } else if (task.type === 'fiction') {
    fileType = 'md'
  }

  api.downloadTaskFile(taskId, fileType)
}

const cancelTask = async (taskId) => {
  if (!confirm('确定要取消这个任务吗？')) return

  try {
    await api.cancelTask(taskId)
    await loadTasks()
  } catch (err) {
    error.value = err.message
  }
}

const deleteTask = async (taskId) => {
  if (!confirm('确定要删除这个任务吗？此操作不可恢复！')) return

  try {
    await api.cancelTask(taskId)
    tasks.value = tasks.value.filter(t => t.task_id !== taskId)
  } catch (err) {
    error.value = err.message
  }
}


// 自动刷新运行中的任务
const startAutoRefresh = () => {
  refreshInterval = setInterval(() => {
    const hasRunningTasks = tasks.value.some(
      task => task.status === 'running' || task.status === 'pending'
    )
    if (hasRunningTasks) {
      loadTasks()
    }
  }, 5000) // 每5秒刷新一次
}

onMounted(() => {
  loadTasks()
  startAutoRefresh()
})

onBeforeUnmount(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.task-monitor {
  max-width: 1000px;
  margin: 0 auto;
}

.description {
  color: #666;
  margin-bottom: 24px;
  font-size: 14px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: 500;
  color: #555;
}

.filter-group select {
  padding: 8px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
}

.loading-section {
  text-align: center;
  padding: 40px;
  color: #666;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-item {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s;
}

.task-item:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.task-item.status-running {
  border-color: #667eea;
  background: linear-gradient(to right, rgba(102, 126, 234, 0.05) 0%, white 100%);
}

.task-item.status-completed {
  border-color: #4caf50;
}

.task-item.status-failed {
  border-color: #f44336;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.task-info {
  display: flex;
  gap: 15px;
  align-items: center;
}

.task-type {
  font-weight: 600;
  color: #333;
  font-size: 16px;
}

.task-id {
  color: #999;
  font-size: 12px;
  font-family: monospace;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.status-running {
  background: #cfe2ff;
  color: #084298;
}

.status-badge.status-completed {
  background: #d1e7dd;
  color: #0f5132;
}

.status-badge.status-failed {
  background: #f8d7da;
  color: #842029;
}

.task-body h3 {
  color: #333;
  margin-bottom: 10px;
  font-size: 18px;
}

.task-meta {
  display: flex;
  gap: 20px;
  color: #666;
  font-size: 13px;
  margin-bottom: 10px;
}

.task-progress {
  margin: 15px 0;
}

.progress-info {
  text-align: center;
  color: #667eea;
  font-size: 13px;
  margin-top: 8px;
}

.task-error {
  background: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 6px;
  margin-top: 10px;
  font-size: 14px;
}

.task-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-state p:first-child {
  font-size: 48px;
  margin-bottom: 10px;
}

.empty-hint {
  color: #666;
  font-size: 14px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  color: #667eea;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.detail-section p {
  margin: 8px 0;
  color: #555;
}

.result-preview {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 2px solid #f0f0f0;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    gap: 15px;
  }

  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .task-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }

  .task-meta {
    flex-direction: column;
    gap: 5px;
  }

  .task-actions {
    flex-wrap: wrap;
  }

  .task-actions button {
    flex: 1;
    min-width: 120px;
  }
}
</style>
