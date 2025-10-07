# XunLong Web UI

XunLong项目的Web前端界面，提供友好的用户交互体验。

## 功能特性

### 📊 报告生成器
- 基于主题自动生成专业研究报告
- 支持多种报告类型（研究报告、分析报告、总结报告、技术报告）
- 支持中英文生成
- 可选包含图片和图表
- 支持HTML和Markdown格式导出

### 📖 小说创作器
- AI驱动的创意小说生成
- 支持多种类型（科幻、奇幻、言情、悬疑、历史、都市）
- 多种写作风格（现代、古典、诗意、简洁）
- 可自定义章节数量
- 章节预览和导出功能

### 🎬 PPT生成器
- 基于主题自动生成PPT演示文稿
- 多种模板风格（专业商务、创意设计、简约、学术）
- 丰富的配色方案
- 自动添加相关图片（可选）
- 支持PPTX和PDF格式导出

### 📋 任务监控
- 实时查看所有任务状态
- 任务进度跟踪
- 任务结果预览
- 任务管理（取消、删除）
- 按状态筛选任务

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **HTTP客户端**: Axios
- **工具库**: VueUse
- **样式**: 原生CSS

## 快速开始

### 环境要求

- Node.js 16+
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 配置环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑`.env`文件，配置API服务器地址：

```env
VITE_API_URL=http://localhost:8000
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173 即可使用Web界面。

### 构建生产版本

```bash
npm run build
```

构建产物将生成在`dist`目录。

### 预览生产版本

```bash
npm run preview
```

## 项目结构

```
web/
├── public/              # 静态资源
├── src/
│   ├── api/            # API接口定义
│   │   └── index.js    # API客户端配置
│   ├── components/     # Vue组件
│   │   ├── ReportGenerator.vue    # 报告生成器组件
│   │   ├── FictionWriter.vue      # 小说创作器组件
│   │   ├── PPTCreator.vue         # PPT生成器组件
│   │   └── TaskMonitor.vue        # 任务监控组件
│   ├── App.vue         # 主应用组件
│   ├── main.js         # 应用入口
│   └── style.css       # 全局样式
├── .env                # 环境变量（不提交到git）
├── .env.example        # 环境变量示例
├── index.html          # HTML模板
├── package.json        # 项目配置
└── vite.config.js      # Vite配置
```

## API接口

Web应用与后端API交互，主要接口包括：

- `POST /api/v1/tasks/report` - 创建报告生成任务
- `POST /api/v1/tasks/fiction` - 创建小说创作任务
- `POST /api/v1/tasks/ppt` - 创建PPT生成任务
- `GET /api/v1/tasks/{task_id}` - 获取任务状态
- `GET /api/v1/tasks/{task_id}/result` - 获取任务结果
- `GET /api/v1/tasks/{task_id}/download` - 下载任务文件
- `DELETE /api/v1/tasks/{task_id}` - 取消/删除任务
- `GET /api/v1/tasks` - 列出所有任务

## 使用说明

### 生成报告

1. 点击顶部导航栏的"Report"标签
2. 填写报告主题和相关参数
3. 点击"生成报告"按钮
4. 等待任务完成，查看进度
5. 完成后可下载HTML或Markdown格式

### 创作小说

1. 切换到"Fiction"标签
2. 输入小说标题和主题描述
3. 选择小说类型、风格和章节数
4. 点击"开始创作"
5. 可在章节列表中预览每一章内容

### 生成PPT

1. 选择"PPT"标签
2. 输入PPT主题和大纲
3. 选择模板风格和配色方案
4. 设置幻灯片数量
5. 点击"生成PPT"并等待完成
6. 下载PPTX或PDF格式文件

### 监控任务

1. 点击"Tasks"标签查看所有任务
2. 使用状态筛选器过滤任务
3. 查看运行中任务的实时进度
4. 点击"查看结果"预览任务输出
5. 可以取消运行中的任务或删除已完成的任务

## 开发指南

### 添加新组件

1. 在`src/components/`目录创建新的Vue组件
2. 在`App.vue`中引入并注册组件
3. 更新导航标签和路由逻辑

### 添加新API

1. 在`src/api/index.js`中添加API方法
2. 使用`apiClient`发送请求
3. 在组件中导入并使用API方法

### 样式自定义

- 全局样式在`App.vue`的`<style>`部分
- 组件样式使用`scoped`样式
- 统一的颜色主题：紫色渐变 (`#667eea` 到 `#764ba2`)

## 注意事项

1. **环境变量**: 确保正确配置`.env`文件中的API地址
2. **后端服务**: Web应用需要后端API服务正常运行
3. **跨域问题**: 开发环境下Vite会自动处理CORS，生产环境需要配置nginx或后端CORS
4. **轮询机制**: 任务状态通过轮询获取，注意控制轮询频率
5. **文件下载**: 大文件下载可能需要较长时间，请耐心等待

## 浏览器兼容性

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

MIT

## 相关链接

- [XunLong主项目](https://github.com/jaguarliuu/xunlong)
- [API文档](../docs/api-usage.md)
- [项目文档](../docs/)
