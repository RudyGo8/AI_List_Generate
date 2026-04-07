<template>
  <section class="workspace shop-workspace">
    <div class="panel">
      <h3>商品生成</h3>

      <label>站点</label>
      <input v-model="site" placeholder="tiktok" />

      <label>目标语言</label>
      <input v-model="desLangType" placeholder="中文" />

      <div class="mode-switch">
        <button class="mode-btn" :class="{ active: inputMode === 'manual' }" type="button" @click="inputMode = 'manual'">
          主图+标题模式
        </button>
        <button class="mode-btn" :class="{ active: inputMode === 'url' }" type="button" @click="inputMode = 'url'">
          链接抓取模式
        </button>
      </div>

      <template v-if="inputMode === 'manual'">
        <label>主图 URL</label>
        <input v-model="spuImageUrl" />
        <label>商品标题</label>
        <input v-model="productTitle" />
        <label>原始类目（可选）</label>
        <input v-model="categoryName" />
      </template>

      <template v-else>
        <label>商品链接 product_url</label>
        <input v-model="productUrl" placeholder="https://..." />
      </template>

      <label>回调地址（可选）</label>
      <input v-model="noticeUrl" placeholder="http://..." />

      <div class="actions">
        <button :disabled="loading" @click="runShop">开始生成</button>
      </div>

      <p class="muted">入参规则：`site` 必填，且 `product_url` 与 `spu_image_url` 至少提供一个。</p>
      <p class="muted" v-if="polling">任务处理中，正在轮询：{{ currentTaskId }}</p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <div class="panel">
      <h3>生成结果</h3>

      <div class="result-grid" v-if="summary">
        <div class="result-card">
          <p class="result-label">任务ID</p>
          <p class="result-value">{{ summary.taskId || '-' }}</p>
        </div>
        <div class="result-card">
          <p class="result-label">状态</p>
          <p class="result-value">{{ summary.statusText }}</p>
        </div>
        <div class="result-card">
          <p class="result-label">模型</p>
          <p class="result-value">{{ summary.modelName || '-' }}</p>
        </div>
        <div class="result-card">
          <p class="result-label">最终类目</p>
          <p class="result-value">{{ summary.categoryText || '-' }}</p>
        </div>
        <div class="result-card">
          <p class="result-label">总用量 Tokens</p>
          <p class="result-value">{{ summary.totalTokens }}</p>
        </div>
        <div class="result-card">
          <p class="result-label">本次耗时</p>
          <p class="result-value">{{ summary.latencyMs }} ms</p>
        </div>
      </div>
      <p v-else class="muted">暂无结果，请先执行一次生成。</p>

      <div class="result-detail" v-if="summary">
        <h4>标题</h4>
        <textarea readonly rows="3" :value="summary.productTitle || '-'"></textarea>

        <h4>描述</h4>
        <textarea readonly rows="7" :value="summary.productDesc || '-'"></textarea>

        <h4>属性</h4>
        <textarea readonly rows="6" :value="summary.attrText || '-'"></textarea>
      </div>

      <JsonCard v-if="result" title="原始响应（调试）" :data="result" />
    </div>

    <div class="panel">
      <h3>最近记录</h3>

      <table class="table" v-if="history.length">
        <thead>
          <tr>
            <th>时间</th>
            <th>状态</th>
            <th>task_id</th>
            <th>耗时(ms)</th>
            <th>tokens</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in history" :key="item.id">
            <td>{{ item.time }}</td>
            <td>
              <span class="status" :class="item.ok ? 'ok' : item.processing ? 'wait' : 'err'">
                {{ item.ok ? '成功' : item.processing ? '处理中' : '失败' }}
              </span>
            </td>
            <td>{{ item.taskId || '-' }}</td>
            <td>{{ item.ms }}</td>
            <td>{{ item.tokens }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="muted">暂无历史记录</p>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import JsonCard from '../components/JsonCard.vue'
import { createShopTask, getShopTask } from '../api/client.js'

const STATUS_TEXT = {
  '00': '成功',
  '01': '失败',
  '02': '排队中',
  '03': '处理中'
}

const inputMode = ref('manual')
const site = ref('tiktok')
const desLangType = ref('中文')
const productUrl = ref('')
const spuImageUrl = ref('https://github.com/RudyGo8/AI_List_Generate/blob/master/datasets/iphone.png?raw=true')
const productTitle = ref('iphone18')
const categoryName = ref('')
const noticeUrl = ref('')

const loading = ref(false)
const polling = ref(false)
const currentTaskId = ref('')
const error = ref('')
const result = ref(null)
const history = ref([])
const latestLatencyMs = ref('-')

const summary = computed(() => {
  const resp = result.value
  if (!resp || !resp.data) return null

  const data = resp.data
  const usage = resp.usage || {}
  const catName = data.category_name || data.category_path || ''
  const catId = data.category_id || ''
  const categoryText = [catName, catId ? `(${catId})` : ''].filter(Boolean).join(' ')
  const statusCode = data.status || ''

  return {
    taskId: data.task_id || '',
    statusText: STATUS_TEXT[statusCode] || statusCode || '-',
    modelName: data.model_name || '',
    categoryText,
    productTitle: data.product_title || '',
    productDesc: data.product_desc || '',
    attrText: data.attr_value_list || data.sales_attr_value_list || '',
    totalTokens: usage.total_tokens ?? 0,
    latencyMs: latestLatencyMs.value
  }
})

function pushHistory(ok, processing, taskId, ms, tokens) {
  history.value.unshift({
    id: `${Date.now()}-${Math.random()}`,
    time: new Date().toLocaleTimeString(),
    ok,
    processing,
    taskId,
    ms,
    tokens
  })
  history.value = history.value.slice(0, 12)
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function buildPayload() {
  const base = {
    site: site.value.trim(),
    des_lang_type: desLangType.value.trim() || '中文',
    notice_url: noticeUrl.value.trim() || undefined
  }

  if (!base.site) {
    throw new Error('site 必填')
  }

  if (inputMode.value === 'url') {
    if (!productUrl.value.trim()) {
      throw new Error('链接抓取模式下必须填写 product_url')
    }
    return {
      ...base,
      product_url: productUrl.value.trim()
    }
  }

  if (!spuImageUrl.value.trim()) {
    throw new Error('主图+标题模式下必须填写 spu_image_url')
  }
  if (!productTitle.value.trim()) {
    throw new Error('主图+标题模式下必须填写 product_title')
  }

  return {
    ...base,
    spu_image_url: spuImageUrl.value.trim(),
    product_title: productTitle.value.trim(),
    category_name: categoryName.value.trim() || undefined
  }
}

async function pollTask(taskId) {
  polling.value = true
  currentTaskId.value = String(taskId)
  const startedAt = performance.now()
  const maxWaitMs = 240000
  const intervalMs = 2500

  while (performance.now() - startedAt < maxWaitMs) {
    const taskResp = await getShopTask(taskId)
    result.value = taskResp
    const status = taskResp?.data?.status

    if (status === '00') {
      const elapsed = Math.round(performance.now() - startedAt)
      latestLatencyMs.value = elapsed
      pushHistory(true, false, taskId, elapsed, taskResp?.usage?.total_tokens ?? 0)
      polling.value = false
      return
    }

    if (status === '01') {
      const elapsed = Math.round(performance.now() - startedAt)
      latestLatencyMs.value = elapsed
      pushHistory(false, false, taskId, elapsed, taskResp?.usage?.total_tokens ?? 0)
      polling.value = false
      error.value = taskResp?.msg || '任务失败'
      return
    }

    await sleep(intervalMs)
  }

  polling.value = false
  error.value = `轮询超时：task_id=${taskId}`
  pushHistory(false, true, taskId, maxWaitMs, 0)
}

async function runShop() {
  loading.value = true
  error.value = ''
  result.value = null

  try {
    const payload = buildPayload()
    const createResp = await createShopTask(payload)
    result.value = createResp

    if (!createResp?.success) {
      error.value = createResp?.msg || '任务创建失败'
      pushHistory(false, false, null, 0, 0)
      return
    }

    const taskId = createResp?.data?.task_id
    if (!taskId) {
      error.value = '未返回 task_id'
      pushHistory(false, false, null, 0, 0)
      return
    }

    pushHistory(false, true, taskId, 0, 0)
    await pollTask(taskId)
  } catch (e) {
    error.value = String(e)
    pushHistory(false, false, null, 0, 0)
  } finally {
    loading.value = false
  }
}
</script>
