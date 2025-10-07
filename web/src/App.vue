<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <div class="logo">
          <h1>🐉 XunLong</h1>
          <p class="tagline">AI-Powered Content Generation</p>
        </div>
        <nav class="nav">
          <a
            v-for="tab in tabs"
            :key="tab.id"
            :class="['nav-item', { active: currentTab === tab.id }]"
            @click="currentTab = tab.id"
          >
            {{ tab.icon }} {{ tab.name }}
          </a>
        </nav>
      </div>
    </header>

    <main class="app-main">
      <div class="container">
        <component
          :is="currentComponent"
          :taskId="currentTaskId"
          @select-mode="handleModeSelect"
          @view-task="handleViewTask"
          @back="handleBackFromTask"
        />
      </div>
    </main>

    <footer class="app-footer">
      <div class="container">
        <p>© 2025 XunLong - AI-Powered Multi-Modal Content Generation</p>
        <a href="https://github.com/jaguarliuu/xunlong" target="_blank">GitHub</a>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import HomePage from './components/HomePage.vue'
import ReportGenerator from './components/ReportGenerator.vue'
import FictionWriter from './components/FictionWriter.vue'
import PPTCreator from './components/PPTCreator.vue'
import TaskMonitor from './components/TaskMonitor.vue'
import TaskDetailView from './components/TaskDetailView.vue'

const currentTab = ref('home')
const currentTaskId = ref(null)

const tabs = [
  { id: 'home', name: '首页', icon: '🏠' },
  { id: 'report', name: '报告', icon: '📊' },
  { id: 'fiction', name: '小说', icon: '📖' },
  { id: 'ppt', name: 'PPT', icon: '🎬' },
  { id: 'tasks', name: '任务', icon: '📋' }
]

const currentComponent = computed(() => {
  // 如果在查看任务详情
  if (currentTaskId.value) {
    return TaskDetailView
  }

  const components = {
    home: HomePage,
    report: ReportGenerator,
    fiction: FictionWriter,
    ppt: PPTCreator,
    tasks: TaskMonitor
  }
  return components[currentTab.value]
})

const handleModeSelect = (modeId) => {
  currentTab.value = modeId
  currentTaskId.value = null
}

const handleViewTask = (taskId) => {
  currentTaskId.value = taskId
}

const handleBackFromTask = () => {
  currentTaskId.value = null
  currentTab.value = 'tasks'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Header */
.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.app-header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.logo h1 {
  font-size: 28px;
  color: #667eea;
  margin-bottom: 4px;
}

.tagline {
  font-size: 12px;
  color: #666;
}

.nav {
  display: flex;
  gap: 10px;
}

.nav-item {
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  color: #666;
  text-decoration: none;
}

.nav-item:hover {
  background: #f0f0f0;
  color: #333;
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

/* Main */
.app-main {
  flex: 1;
  padding: 40px 0;
}

/* Footer */
.app-footer {
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 20px 0;
  text-align: center;
}

.app-footer .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-footer a {
  color: #667eea;
  text-decoration: none;
}

.app-footer a:hover {
  text-decoration: underline;
}

/* Common Card Style */
.card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.card h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

/* Form Styles */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.form-group textarea {
  min-height: 120px;
  resize: vertical;
}

/* Button Styles */
.btn {
  padding: 12px 30px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

/* Progress Bar */
.progress-bar {
  width: 100%;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin: 10px 0;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s;
}

/* Alert */
.alert {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.alert-success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alert-info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

/* Loading Spinner */
.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
