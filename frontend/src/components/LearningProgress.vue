<script setup lang="ts">
import { useI18n } from "vue-i18n";
import type { LearningSummary } from "../types";
defineProps<{ summary: LearningSummary }>();
const { t } = useI18n();
</script>
<template>
  <div class="learning-progress">
    <div class="progress-label">
      <span>{{
        t("learning.done", {
          done: summary.completed_count,
          total: summary.total_count,
        })
      }}</span
      ><strong>{{ summary.percent }}%</strong>
    </div>
    <progress
      :value="summary.percent"
      max="100"
      :aria-label="t('learning.progress')"
    ></progress>
    <p>
      <span>{{ t(`learning.${summary.state}`) }}</span
      ><span v-if="summary.best_score !== null">
        · {{ t("learning.best", { score: summary.best_score }) }}</span
      >
    </p>
  </div>
</template>
