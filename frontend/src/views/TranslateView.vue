<template>
  <section class="workspace">
    <div class="panel">
      <h3>文本翻译</h3>
      <label>目标语言</label>
      <input v-model="desLangType" placeholder="English" />
      <label>内容（批量时每行一条）</label>
      <textarea v-model="content" rows="6" />
      <div class="actions">
        <button :disabled="loading" @click="runSingle">单条翻译</button>
        <button class="alt" :disabled="loading" @click="runBatch">批量翻译</button>
      </div>
      <p class="muted">接口：`/api/r1/c/translate`、`/api/r1/c/batchtranslate`</p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <div class="panel">
      <h3>调用记录</h3>
      <table class="table" v-if="history.length">
        <thead>
          <tr><th>时间</th><th>类型</th><th>状态</th><th>耗时(ms)</th></tr>
        </thead>
        <tbody>
          <tr v-for="item in history" :key="item.id">
            <td>{{ item.time }}</td>
            <td>{{ item.mode }}</td>
            <td>
              <span class="status" :class="item.ok ? 'ok' : 'err'">{{ item.ok ? '成功' : '失败' }}</span>
            </td>
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
import { batchTranslate, translate } from '../api/client.js'

const desLangType = ref('English')
const content = ref('Hello from Vue frontend')
const loading = ref(false)
const error = ref('')
const result = ref(null)
const history = ref([])

function pushHistory(mode, ok, ms) {
  history.value.unshift({
    id: `${Date.now()}-${Math.random()}`,
    time: new Date().toLocaleTimeString(),
    mode,
    ok,
    ms
  })
  history.value = history.value.slice(0, 10)
}

async function runSingle() {
  loading.value = true
  error.value = ''
  const start = performance.now()
  try {
    result.value = await translate(content.value, desLangType.value)
    pushHistory('单条', true, Math.round(performance.now() - start))
  } catch (e) {
    error.value = String(e)
    pushHistory('单条', false, Math.round(performance.now() - start))
  } finally {
    loading.value = false
  }
}

async function runBatch() {
  loading.value = true
  error.value = ''
  const start = performance.now()
  try {
    const list = content.value.split('\n').map((x) => x.trim()).filter(Boolean)
    result.value = await batchTranslate(list, desLangType.value)
    pushHistory('批量', true, Math.round(performance.now() - start))
  } catch (e) {
    error.value = String(e)
    pushHistory('批量', false, Math.round(performance.now() - start))
  } finally {
    loading.value = false
  }
}
</script>
