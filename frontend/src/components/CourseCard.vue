<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { Clock3, BookOpen, ArrowUpRight } from "lucide-vue-next";
import type { Course } from "../types";
import CourseCover from "./CourseCover.vue";
defineProps<{ course: Course }>();
const { t } = useI18n();
</script>
<template>
  <RouterLink :to="`/courses/${course.id}`" class="course-card"
    ><CourseCover :kind="course.cover_kind" />
    <div class="course-card-body">
      <div class="card-tags">
        <span>{{ course.category.name }}</span
        ><span class="level"
          ><i></i>{{ t(`common.${course.difficulty}`) }}</span
        >
      </div>
      <h3>{{ course.title }}</h3>
      <p class="card-description">{{ course.description }}</p>
      <div class="card-meta">
        <span
          ><BookOpen :size="14" />{{ course.lesson_count }}
          {{ t("common.lessons") }}</span
        ><span
          ><Clock3 :size="14" />{{ course.duration_minutes }}
          {{ t("common.minutes") }}</span
        >
      </div>
      <div class="card-bottom">
        <span class="free">{{ t("common.free") }}</span
        ><span>{{ t("catalog.view") }}<ArrowUpRight :size="16" /></span>
      </div></div
  ></RouterLink>
</template>
