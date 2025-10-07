<template>
  <div class="home-page">
    <div class="hero-section">
      <div class="hero-content">
        <div class="badge">XunLong 1.0</div>
        <h1 class="title">AI驱动的多模态内容生成平台</h1>
        <p class="subtitle">基于深度搜索技术，生成专业报告、创意小说、精美PPT</p>
      </div>
    </div>

    <div class="modes-section">
      <div class="modes-grid">
        <div
          v-for="mode in modes"
          :key="mode.id"
          class="mode-card"
          @click="selectMode(mode.id)"
        >
          <div class="mode-icon">{{ mode.icon }}</div>
          <h3 class="mode-title">{{ mode.title }}</h3>
          <p class="mode-desc">{{ mode.description }}</p>
        </div>
      </div>
    </div>

    <div class="features-section">
      <h2>核心特性</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">🚀</div>
          <h4>智能生成</h4>
          <p>基于AI大模型，自动生成高质量内容</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h4>深度搜索</h4>
          <p>多源数据聚合，确保内容准确性</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">⚡</div>
          <h4>异步处理</h4>
          <p>后台任务执行，实时进度反馈</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🎨</div>
          <h4>多种格式</h4>
          <p>支持HTML、Markdown、PPT等导出</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const modes = [
  {
    id: 'report',
    icon: '📊',
    title: '报告生成',
    description: '基于深度搜索生成专业研究报告，支持多种类型和格式'
  },
  {
    id: 'fiction',
    icon: '📖',
    title: '小说创作',
    description: 'AI驱动的创意小说生成，支持多种体裁和风格'
  },
  {
    id: 'ppt',
    icon: '🎬',
    title: 'PPT制作',
    description: '自动生成精美PPT演示文稿，多种主题模板'
  },
  {
    id: 'tasks',
    icon: '📋',
    title: '任务管理',
    description: '查看和管理所有任务，实时跟踪执行进度'
  }
]

const emit = defineEmits(['select-mode'])

const selectMode = (modeId) => {
  emit('select-mode', modeId)
}
</script>

<style scoped>
.home-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-section {
  text-align: center;
  padding: 80px 20px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 24px;
  margin-bottom: 60px;
}

.badge {
  display: inline-block;
  padding: 8px 16px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  color: #667eea;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 24px;
}

.title {
  font-size: 48px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 16px;
  line-height: 1.2;
}

.subtitle {
  font-size: 20px;
  color: #666;
  max-width: 600px;
  margin: 0 auto;
}

.modes-section {
  margin-bottom: 80px;
}

.modes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.mode-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid #f0f0f0;
  text-align: center;
}

.mode-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.mode-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.mode-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 12px;
}

.mode-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

.features-section {
  margin-bottom: 60px;
}

.features-section h2 {
  text-align: center;
  font-size: 36px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 48px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 32px;
}

.feature-card {
  text-align: center;
  padding: 24px;
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 16px;
}

.feature-card h4 {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.feature-card p {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .title {
    font-size: 32px;
  }

  .subtitle {
    font-size: 16px;
  }

  .modes-grid {
    grid-template-columns: 1fr;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>
