import { defineConfig } from "vitepress";
import { withMermaid } from "vitepress-plugin-mermaid";

// https://vitepress.dev/reference/site-config
export default withMermaid(
  defineConfig({
    title: "XunLong",
    description: "AI-Powered Multi-Modal Content Generation System",

    // 多语言配置
    locales: {
      root: {
        label: "English",
        lang: "en",
        themeConfig: {
          nav: [
            { text: "Home", link: "/" },
            { text: "Guide", link: "/guide/getting-started" },
            { text: "Tutorials", link: "/tutorial/chapter1-playwright-duckduckgo" },
            { text: "API", link: "/api/cli" },
            { text: "Examples", link: "/examples/report" },
          ],
          sidebar: {
            "/guide/": [
              {
                text: "Introduction",
                items: [
                  { text: "What is XunLong?", link: "/guide/introduction" },
                  { text: "Getting Started", link: "/guide/getting-started" },
                  { text: "Installation", link: "/guide/installation" },
                ],
              },
              {
                text: "Core Concepts",
                items: [
                  { text: "Architecture", link: "/guide/architecture" },
                  { text: "Multi-Agent System", link: "/guide/multi-agent" },
                  { text: "Workflow", link: "/guide/workflow" },
                ],
              },
              {
                text: "Features",
                items: [
                  { text: "Report Generation", link: "/guide/features/report" },
                  { text: "Fiction Writing", link: "/guide/features/fiction" },
                  { text: "PPT Creation", link: "/guide/features/ppt" },
                  {
                    text: "Content Iteration",
                    link: "/guide/features/iteration",
                  },
                  { text: "Export Formats", link: "/guide/features/export" },
                ],
              },
              {
                text: "API Usage",
                items: [
                  { text: "REST API Guide", link: "/guide/api-usage" },
                ],
              },
            ],
            "/api/": [
              {
                text: "Command Line",
                items: [
                  { text: "CLI Reference", link: "/api/cli" },
                  { text: "Configuration", link: "/api/configuration" },
                ],
              },
              {
                text: "REST API",
                items: [
                  { text: "API Guide", link: "/guide/api-usage" },
                ],
              },
            ],
            "/examples/": [
              {
                text: "Examples",
                items: [
                  { text: "Report Generation", link: "/examples/report" },
                  { text: "Fiction Writing", link: "/examples/fiction" },
                  { text: "PPT Creation", link: "/examples/ppt" },
                  { text: "Iteration", link: "/examples/iteration" },
                ],
              },
            ],
          },
          socialLinks: [
            { icon: "github", link: "https://github.com/jaguarliuu/xunlong" },
          ],
          footer: {
            message: "Released under the MIT License.",
            copyright: "Copyright © 2025-present XunLong Team",
          },
        },
      },
      zh: {
        label: "简体中文",
        lang: "zh-CN",
        link: "/zh/",
        themeConfig: {
          nav: [
            { text: "首页", link: "/zh/" },
            { text: "指南", link: "/zh/guide/getting-started" },
            { text: "教程", link: "/tutorial/chapter1-playwright-duckduckgo" },
            { text: "API", link: "/zh/api/cli" },
            { text: "示例", link: "/zh/examples/report" },
          ],
          sidebar: {
            "/zh/guide/": [
              {
                text: "介绍",
                items: [
                  { text: "什么是XunLong？", link: "/zh/guide/introduction" },
                  { text: "快速开始", link: "/zh/guide/getting-started" },
                  { text: "安装", link: "/zh/guide/installation" },
                ],
              },
              {
                text: "核心概念",
                items: [
                  { text: "系统架构", link: "/zh/guide/architecture" },
                  { text: "多智能体系统", link: "/zh/guide/multi-agent" },
                  { text: "工作流程", link: "/zh/guide/workflow" },
                ],
              },
              {
                text: "功能特性",
                items: [
                  { text: "报告生成", link: "/zh/guide/features/report" },
                  { text: "小说创作", link: "/zh/guide/features/fiction" },
                  { text: "PPT制作", link: "/zh/guide/features/ppt" },
                  { text: "内容迭代", link: "/zh/guide/features/iteration" },
                  { text: "导出格式", link: "/zh/guide/features/export" },
                ],
              },
              {
                text: "API使用",
                items: [
                  { text: "REST API指南", link: "/zh/guide/api-usage" },
                ],
              },
            ],
            "/zh/api/": [
              {
                text: "命令行",
                items: [
                  { text: "CLI参考", link: "/zh/api/cli" },
                  { text: "配置", link: "/zh/api/configuration" },
                ],
              },
              {
                text: "REST API",
                items: [
                  { text: "API指南", link: "/zh/guide/api-usage" },
                ],
              },
            ],
            "/zh/examples/": [
              {
                text: "示例",
                items: [
                  { text: "报告生成", link: "/zh/examples/report" },
                  { text: "小说创作", link: "/zh/examples/fiction" },
                  { text: "PPT制作", link: "/zh/examples/ppt" },
                  { text: "内容迭代", link: "/zh/examples/iteration" },
                ],
              },
            ],
          },
          socialLinks: [
            { icon: "github", link: "https://github.com/jaguarliuu/xunlong" },
          ],
          footer: {
            message: "基于MIT许可证发布",
            copyright: "Copyright © 2025-present XunLong Team",
          },
          docFooter: {
            prev: "上一页",
            next: "下一页",
          },
          outline: {
            label: "页面导航",
          },
          lastUpdated: {
            text: "最后更新于",
            formatOptions: {
              dateStyle: "short",
              timeStyle: "medium",
            },
          },
          returnToTopLabel: "回到顶部",
          sidebarMenuLabel: "菜单",
          darkModeSwitchLabel: "主题",
          lightModeSwitchTitle: "切换到浅色模式",
          darkModeSwitchTitle: "切换到深色模式",
        },
      },
    },

    // 主题配置
    themeConfig: {
      logo: "/icon.png",
      search: {
        provider: "local",
      },
    },

    // Markdown配置
    markdown: {
      lineNumbers: true,
      config: (md) => {
        // Mermaid support will be added via plugin
      },
    },

    // 构建配置
    base: "/xunlong/", // GitHub Pages部署时需要，改为你的仓库名
    lastUpdated: true,
    cleanUrls: true,
    ignoreDeadLinks: true, // 忽略死链接检查
  })
);
