<script setup lang="ts">
import { useI18n } from "vue-i18n";
import type { Course } from "../types";
defineProps<{ course: Course }>();
const { t } = useI18n();
</script>
<template>
  <RouterLink class="course-card" :to="`/courses/${course.id}`"
    ><div class="card-tags">
      <span>{{ course.category.name }}</span
      ><span>{{ t(`common.${course.difficulty}`) }}</span>
    </div>
    <h3>{{ course.title }}</h3>
    <p>{{ course.description }}</p>
    <div class="card-meta">
      <span
        >{{ course.lesson_count }} {{ t("common.lessons") }} ·
        {{ course.duration_minutes }} {{ t("common.minutes") }}</span
      ><strong>{{ t("common.free") }}</strong>
    </div>
    <span class="text-link">{{ t("catalog.view") }} →</span></RouterLink
  >
</template>
