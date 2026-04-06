<template>
  <div class="json-card">
    <div class="json-head">
      <strong>{{ title }}</strong>
    </div>
    <pre>{{ formatted }}</pre>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  data: { type: null, default: null }
})

const formatted = computed(() => JSON.stringify(props.data, null, 2))
</script>
