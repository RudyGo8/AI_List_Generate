<template>
  <section class="workspace shop-workspace">
    <div class="panel">
      <h3>商品生成</h3>

      <label>站点</label>
      <input v-model.trim="site" placeholder="shop / tiktok" />

      <label>目标语言</label>
      <input v-model.trim="desLangType" placeholder="English / 中文" />

      <div class="mode-switch">
        <button class="mode-btn" :class="{ active: inputMode === 'manual' }" type="button" @click="inputMode = 'manual'">
          主图+标题
        </button>
        <button class="mode-btn" :class="{ active: inputMode === 'url' }" type="button" @click="inputMode = 'url'">
          商品链接
        </button>
      </div>

      <template v-if="inputMode === 'manual'">
        <label>主图 URL</label>
        <input v-model.trim="spuImageUrl" placeholder="https://..." />

        <label>商品标题</label>
        <input v-model.trim="productTitle" placeholder="例如：iPhone 15 128GB Unlocked" />

        <label>原始类目（可选）</label>
        <input v-model.trim="categoryName" placeholder="Electronics > Mobile Phones" />
      </template>

      <template v-else>
        <label>product_url</label>
        <input v-model.trim="productUrl" placeholder="https://..." />
      </template>

      <label>回调地址（可选）</label>
      <input v-model.trim="noticeUrl" placeholder="http://..." />

      <div class="actions">
        <button :disabled="submitDisabled" @click="runShop">
          {{ loading ? '提交中...' : '开始生成' }}
        </button>
        <button class="alt" type="button" :disabled="loading || polling" @click="fillDemo">填充示例</button>
      </div>

      <p class="muted">入参规则：必须填写 site，且 product_url 与 spu_image_url 二选一。</p>
      <p class="muted" v-if="polling">任务处理中（task_id={{ currentTaskId }}）</p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <div class="panel">
      <h3>生成结果</h3>

      <div class="result-grid" v-if="summary">
        <div class="result-card">
          <p class="result-label">状态</p>
          <p class="result-value">
            <span class="status" :class="statusClass(summary.statusCode)">{{ summary.statusText }}</span>
          </p>
        </div>
        <div class="result-card">
          <p class="result-label">任务ID</p>
          <p class="result-value">{{ summary.taskId || '-' }}</p>
        </div>
        <div class="result-card">
          <p class="result-label">模型</p>
          <p class="result-value">{{ summary.modelName || '-' }}</p>
        </div>
        <div class="result-card">
          <p class="result-label">类目</p>
          <p class="result-value">{{ summary.categoryText || '-' }}</p>
        </div>
        <div class="result-card">
          <p class="result-label">总耗时</p>
          <p class="result-value">{{ summary.totalMsText }}</p>
        </div>
        <div class="result-card">
          <p class="result-label">总 Tokens</p>
          <p class="result-value">{{ summary.totalTokens }}</p>
        </div>
      </div>
      <p v-else class="muted">暂无结果，请先执行一次生成。</p>

      <div class="result-detail" v-if="summary">
        <h4>标题</h4>
        <textarea readonly class="auto-grow" :rows="rowCount(summary.productTitle, 2, 8)" :value="summary.productTitle || '-'" />

        <h4>描述</h4>
        <textarea readonly class="auto-grow" :rows="rowCount(summary.productDesc, 5, 24)" :value="summary.productDesc || '-'" />

        <h4>属性</h4>
        <div v-if="parsedAttributes.length" class="attr-grid">
          <div v-for="attr in parsedAttributes" :key="`${attr.key}-${attr.value}`" class="attr-item">
            <p class="attr-key">{{ attr.key }}</p>
            <p class="attr-value">{{ attr.value }}</p>
          </div>
        </div>
        <textarea v-else readonly class="auto-grow" :rows="rowCount(summary.attrText, 4, 18)" :value="summary.attrText || '-'" />
      </div>
    </div>

    <div class="panel">
      <h3>最近记录</h3>

      <table class="table" v-if="history.length">
        <thead>
          <tr>
            <th>时间</th>
            <th>状态</th>
            <th>task_id</th>
            <th>总耗时(ms)</th>
            <th>tokens</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in history" :key="item.id" class="clickable-row" @click="restoreHistory(item)">
            <td>{{ item.time }}</td>
            <td>
              <span class="status" :class="statusClass(item.status)">{{ STATUS_TEXT[item.status] || item.status }}</span>
            </td>
            <td>{{ item.taskId || '-' }}</td>
            <td>{{ item.ms }}</td>
            <td>{{ item.tokens }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="muted">暂无历史记录。</p>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { createShopTask, getShopTask } from '../api/client.js'

const STATUS_TEXT = {
  '00': '成功',
  '01': '失败',
  '02': '排队中',
  '03': '处理中'
}

const inputMode = ref('manual')
const site = ref('shop')
const desLangType = ref('English')
const productUrl = ref('')
const spuImageUrl = ref('https://github.com/RudyGo8/AI_List_Generate/blob/master/datasets/iphone.png?raw=true')
const productTitle = ref('Apple iPhone smartphone 128GB unlocked')
const categoryName = ref('')
const noticeUrl = ref('')

const loading = ref(false)
const polling = ref(false)
const currentTaskId = ref('')
const error = ref('')
const result = ref(null)
const history = ref([])
const latestTotalMs = ref(0)

const submitDisabled = computed(() => {
  if (loading.value || polling.value) return true
  if (!site.value.trim()) return true
  if (inputMode.value === 'url') {
    return !productUrl.value.trim()
  }
  return !spuImageUrl.value.trim() || !productTitle.value.trim()
})

const summary = computed(() => {
  const resp = result.value
  if (!resp || !resp.data) return null

  const data = resp.data
  const usage = resp.usage || {}
  const statusCode = data.status || ''
  const catName = data.category_name || data.category_path || ''
  const catId = data.category_id || ''

  return {
    taskId: data.task_id || '',
    statusCode,
    statusText: STATUS_TEXT[statusCode] || statusCode || '-',
    modelName: data.model_name || '',
    categoryText: [catName, catId ? `(${catId})` : ''].filter(Boolean).join(' '),
    productTitle: data.product_title || '',
    productDesc: data.product_desc || '',
    attrText: data.attr_value_list || data.sales_attr_value_list || '',
    totalTokens: usage.total_tokens ?? 0,
    totalMsText: latestTotalMs.value ? `${latestTotalMs.value} ms` : '-'
  }
})

const parsedAttributes = computed(() => {
  if (!summary.value?.attrText) return []
  const raw = String(summary.value.attrText).trim()
  if (!raw) return []

  const rows = []
  try {
    const obj = JSON.parse(raw)
    if (Array.isArray(obj)) {
      obj.forEach((item, idx) => {
        if (item && typeof item === 'object') {
          Object.entries(item).forEach(([k, v]) => rows.push({ key: k, value: String(v ?? '') }))
        } else {
          rows.push({ key: `属性${idx + 1}`, value: String(item) })
        }
      })
      return rows.slice(0, 30)
    }
    if (obj && typeof obj === 'object') {
      Object.entries(obj).forEach(([k, v]) => rows.push({ key: k, value: String(v ?? '') }))
      return rows.slice(0, 30)
    }
  } catch (_) {
    return []
  }
  return []
})

function statusClass(code) {
  if (code === '00') return 'ok'
  if (code === '01') return 'err'
  return 'wait'
}

function fillDemo() {
  inputMode.value = 'manual'
  site.value = 'shop'
  desLangType.value = 'English'
  spuImageUrl.value = 'https://github.com/RudyGo8/AI_List_Generate/blob/master/datasets/iphone.png?raw=true'
  productTitle.value = 'Apple iPhone smartphone 128GB unlocked'
  categoryName.value = ''
  noticeUrl.value = ''
}

function pushHistory(status, taskId, ms, tokens) {
  history.value.unshift({
    id: `${Date.now()}-${Math.random()}`,
    time: new Date().toLocaleTimeString(),
    status,
    taskId,
    ms,
    tokens,
    snapshot: result.value ? JSON.parse(JSON.stringify(result.value)) : null
  })
  history.value = history.value.slice(0, 12)
}

function restoreHistory(item) {
  if (!item?.snapshot) return
  result.value = item.snapshot
  latestTotalMs.value = Number(item.ms) || 0
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function buildPayload() {
  const base = {
    site: site.value.trim(),
    des_lang_type: desLangType.value.trim() || 'English',
    notice_url: noticeUrl.value.trim() || undefined
  }

  if (inputMode.value === 'url') {
    return {
      ...base,
      product_url: productUrl.value.trim()
    }
  }

  return {
    ...base,
    spu_image_url: spuImageUrl.value.trim(),
    product_title: productTitle.value.trim(),
    category_name: categoryName.value.trim() || undefined
  }
}

function parseError(err) {
  if (!err) return '未知错误'
  const msg = String(err)
  if (msg.includes('401')) return '鉴权失败，请检查 accesskey/accesssecret'
  return msg
}

function rowCount(text, minRows = 3, maxRows = 20) {
  const value = String(text || '')
  const lineCount = value.split('\n').length
  const lengthBased = Math.ceil(value.length / 36)
  const rows = Math.max(lineCount, lengthBased, minRows)
  return Math.min(rows, maxRows)
}

async function pollTask(taskId) {
  polling.value = true
  currentTaskId.value = String(taskId)
  const startedAt = performance.now()
  const maxWaitMs = 240000
  const intervals = [1600, 2200, 3000, 4000, 5000]
  let attempt = 0

  while (performance.now() - startedAt < maxWaitMs) {
    const taskResp = await getShopTask(taskId)
    result.value = taskResp

    const status = taskResp?.data?.status
    if (status === '00' || status === '01') {
      const elapsed = Math.round(performance.now() - startedAt)
      latestTotalMs.value = elapsed
      pushHistory(status, taskId, elapsed, taskResp?.usage?.total_tokens ?? 0)
      polling.value = false
      if (status === '01') {
        error.value = taskResp?.msg || '任务失败'
      }
      return
    }

    const sleepMs = intervals[Math.min(attempt, intervals.length - 1)]
    attempt += 1
    await sleep(sleepMs)
  }

  polling.value = false
  latestTotalMs.value = maxWaitMs
  error.value = `轮询超时，task_id=${taskId}`
  pushHistory('01', taskId, maxWaitMs, 0)
}

async function runShop() {
  loading.value = true
  error.value = ''
  result.value = null
  latestTotalMs.value = 0

  try {
    const payload = buildPayload()
    const createResp = await createShopTask(payload)
    result.value = createResp

    if (!createResp?.success) {
      error.value = createResp?.msg || '任务创建失败'
      pushHistory('01', null, 0, 0)
      return
    }

    const taskId = createResp?.data?.task_id
    if (!taskId) {
      error.value = '未返回 task_id'
      pushHistory('01', null, 0, 0)
      return
    }

    pushHistory('03', taskId, 0, 0)
    await pollTask(taskId)
  } catch (e) {
    error.value = parseError(e)
    pushHistory('01', null, 0, 0)
  } finally {
    loading.value = false
  }
}
</script>
