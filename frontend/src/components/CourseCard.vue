<script setup lang="ts">
import { useI18n } from "vue-i18n";
import type { Course } from "../types";
import { ArrowUpRight, Braces, Code2, Terminal } from "lucide-vue-next";
defineProps<{ course: Course }>();
const { t } = useI18n();
</script>
<template>
  <RouterLink class="course-card" :to="`/courses/${course.id}`"
    ><div
      class="course-cover"
      :class="`cover-${course.cover_kind}`"
      aria-hidden="true"
    >
      <span class="cover-label">{{
        course.cover_kind === "javascript"
          ? "JAVASCRIPT"
          : course.cover_kind === "python"
            ? "PYTHON"
            : "WEB DEVELOPMENT"
      }}</span>
      <Braces
        v-if="course.cover_kind === 'javascript'"
        :size="42"
        :stroke-width="1.2"
      /><Terminal
        v-else-if="course.cover_kind === 'python'"
        :size="42"
        :stroke-width="1.2"
      /><Code2 v-else :size="42" :stroke-width="1.2" />
      <span class="cover-code">{{
        course.cover_kind === "javascript"
          ? "const learn = () => grow;"
          : course.cover_kind === "python"
            ? 'print("Hello, world!")'
            : "&lt;build your future /&gt;"
      }}</span>
    </div>
    <div class="card-tags">
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
    <span class="text-link card-link"
      >{{ t("catalog.view")
      }}<ArrowUpRight :size="16" aria-hidden="true" /></span
  ></RouterLink>
</template>
