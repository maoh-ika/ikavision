import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import markdown from 'vite-plugin-md'
import markdownItPrism from 'markdown-it-prism'
import markdownItAnchor from 'markdown-it-anchor'
import { link, code } from 'md-powerpack'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue({ include: [/\.vue$/, /\.md$/] }),
    markdown({
      markdownItOptions: {
      },
      markdownItSetup(md) {
        md.use(markdownItAnchor)
        md.use(markdownItPrism)
      },
      builders: [
        link(),
        code({
          theme: 'base',
          engine: 'Prism'
        })
      ]
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
