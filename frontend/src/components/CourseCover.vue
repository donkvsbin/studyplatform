<script setup lang="ts">
import { Code2, Braces, Terminal, ArrowUpRight } from "lucide-vue-next";
defineProps<{ kind: string; large?: boolean }>();
</script>
<template>
  <div :class="['course-cover', kind, { large }]" aria-hidden="true">
    <div class="cover-grid"></div>
    <span class="cover-label">{{
      kind === "web"
        ? "BUILD FOR THE WEB"
        : kind === "javascript"
          ? "MAKE THINGS HAPPEN"
          : "THINK. CODE. CREATE."
    }}</span>
    <div class="cover-symbol">
      <Code2 v-if="kind === 'web'" :size="66" :stroke-width="1.3" /><Braces
        v-else-if="kind === 'javascript'"
        :size="66"
        :stroke-width="1.3"
      /><Terminal v-else :size="66" :stroke-width="1.3" />
    </div>
    <span class="cover-tag">{{
      kind === "web"
        ? "HTML + CSS"
        : kind === "javascript"
          ? "JavaScript"
          : "Python"
    }}</span
    ><span class="cover-corner"><ArrowUpRight :size="19" /></span
    ><span class="cover-orbit"></span>
  </div>
</template>
