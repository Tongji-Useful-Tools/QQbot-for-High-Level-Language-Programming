import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Question and Answer Collection",
  description: "问与答收集站",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Typical', link: '/typical' },
      { text: 'Document', link: '/document'},
      { text: 'Programming', link: '/programming' },
      { text: 'Technology', link: '/technology' },
      { text: 'Unmeaningful', link: '/unmeaningful' },
      { text: 'Open questions', link: '/open' }
    ],

    sidebar: [
      {
        text: 'Closed',
        items: [
          { text: 'Typical', link: '/typical' },
          { text: 'Document', link: '/document'},
          { text: 'Programming', link: '/programming' },
          { text: 'Technology', link: '/technology' },
          { text: 'Unmeaningful', link: '/unmeaningful' }
        ]
      },
      {
        text: "Open",
        items: [
          { text: "Open questions", link: '/open' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ]
  },
  markdown: {
    image: {
      // 默认禁用；设置为 true 可为所有图片启用懒加载。
      lazyLoading: true
    }
  }
})
