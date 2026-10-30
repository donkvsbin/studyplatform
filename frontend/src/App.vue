<script setup lang="ts">
import { ref, onMounted } from 'vue'
const status = ref('Connecting…')
onMounted(async () => { try { const res = await fetch('/api/v1/health'); status.value = (await res.json()).data.status } catch { status.value = 'Unavailable' } })
</script>
<template><main><h1>LearnHub · 学习坊</h1><p>Vue → Flask → SQLite: {{ status }}</p></main></template>
