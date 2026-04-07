<template>
  <section class="workspace">
    <div class="panel">
      <h3>图片 OCR</h3>
      <label>图片 URL（每行一条）</label>
      <textarea v-model="imageUrls" rows="6" />
      <div class="actions">
        <button :disabled="loading" @click="runOcr">执行识别</button>
      </div>
      <p class="muted">接口：`/api/r1/c/ocr`</p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <div class="panel">
      <h3>调用记录</h3>
      <table class="table" v-if="history.length">
        <thead>
          <tr><th>时间</th><th>图片数</th><th>状态</th><th>耗时(ms)</th></tr>
        </thead>
        <tbody>
          <tr v-for="item in history" :key="item.id">
            <td>{{ item.time }}</td>
            <td>{{ item.count }}</td>
            <td><span class="status" :class="item.ok ? 'ok' : 'err'">{{ item.ok ? '成功' : '失败' }}</span></td>
            <td>{{ item.ms }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="muted">暂无调用记录</p>

      <JsonCard v-if="result" title="最近一次响应" :data="result" />
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import JsonCard from '../components/JsonCard.vue'
import { ocr } from '../api/client.js'

const imageUrls = ref('https://raw.githubusercontent.com/RudyGo8/AI_List_Generate/refs/heads/master/datasets/iphone.png')
const loading = ref(false)
const error = ref('')
const result = ref(null)
const history = ref([])

function pushHistory(count, ok, ms) {
  history.value.unshift({
    id: `${Date.now()}-${Math.random()}`,
    time: new Date().toLocaleTimeString(),
    count,
    ok,
    ms
  })
  history.value = history.value.slice(0, 10)
}

async function runOcr() {
  loading.value = true
  error.value = ''
  const start = performance.now()
  const list = imageUrls.value.split('\n').map((x) => x.trim()).filter(Boolean)
  try {
    result.value = await ocr(list)
    pushHistory(list.length, true, Math.round(performance.now() - start))
  } catch (e) {
    error.value = String(e)
    pushHistory(list.length, false, Math.round(performance.now() - start))
  } finally {
    loading.value = false
  }
}
</script>
