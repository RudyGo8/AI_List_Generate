<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">AI</div>
        <div>
          <h1>Listing ERP</h1>
          <p>Product Ops Console</p>
        </div>
      </div>

      <nav class="menu">
        <p class="menu-title">业务模块</p>
        <RouterLink to="/translate">文本翻译</RouterLink>
        <RouterLink to="/ocr">图片 OCR</RouterLink>
        <RouterLink to="/shop">商品生成</RouterLink>
      </nav>

      <section class="settings card-dark">
        <h2>连接配置</h2>
        <label>AccessKey</label>
        <input v-model="accesskey" @blur="save" />
        <label>AccessSecret</label>
        <input v-model="accesssecret" @blur="save" />
        <label>AI Scene</label>
        <input v-model="scene" @blur="save" />
      </section>
    </aside>

    <main class="main">
      <header class="topbar">
        <div>
          <h2>AI 商品运营控制台</h2>
          <p>统一调用翻译、OCR、商品生成接口</p>
        </div>
        <div class="topbar-badges">
          <span class="badge">Scene: {{ scene }}</span>
          <span class="badge">Env: Local</span>
        </div>
      </header>

      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const accesskey = ref(localStorage.getItem('accesskey') || import.meta.env.VITE_ACCESS_KEY || 'test_key')
const accesssecret = ref(localStorage.getItem('accesssecret') || import.meta.env.VITE_ACCESS_SECRET || 'test_secret')
const scene = ref(localStorage.getItem('ai_scene') || import.meta.env.VITE_AI_SCENE || 'default')

const save = () => {
  localStorage.setItem('accesskey', accesskey.value)
  localStorage.setItem('accesssecret', accesssecret.value)
  localStorage.setItem('ai_scene', scene.value)
}

save()
</script>
