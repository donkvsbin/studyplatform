<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { BookOpen, ArrowUpRight } from "lucide-vue-next";
import { api } from "../api";
import type { Enrollment } from "../types";
import CourseCard from "../components/CourseCard.vue";
import UiError from "../components/UiError.vue";
const { t, locale } = useI18n(),
  rows = ref<Enrollment[]>([]),
  busy = ref(true),
  error = ref<unknown>(null);
let sequence = 0;
async function load() {
  const id = ++sequence;
  busy.value = true;
  error.value = null;
  try {
    const result = await api<{ data: Enrollment[] }>("/me/enrollments");
    if (id === sequence) rows.value = result.data;
  } catch (e) {
    if (id === sequence) error.value = e;
  } finally {
    if (id === sequence) busy.value = false;
  }
}
watch(locale, load, { immediate: true });
</script>
<template>
  <div class="container page learning-page">
    <span class="section-kicker">YOUR LEARNING JOURNEY</span>
    <h1>{{ t("catalog.myTitle") }}</h1>
    <p class="page-subtitle">{{ t("catalog.mySub") }}</p>
    <UiError :error="error" /><button
      v-if="error"
      class="button button-outline"
      @click="load"
    >
      {{ t("common.retry") }}
    </button>
    <p v-if="busy" class="loading-state" role="status">
      {{ t("common.loading") }}
    </p>
    <template v-else-if="!error"
      ><div v-if="rows.length" class="course-grid learning-grid">
        <div v-for="row in rows" :key="row.id">
          <CourseCard v-if="row.available" :course="row.course" />
          <div v-else class="panel withdrawn-course">
            <BookOpen :size="28" />
            <h3>{{ row.course.title }}</h3>
            <p>{{ t("catalog.withdrawn") }}</p>
          </div>
          <p class="joined-date">
            {{ t("catalog.joinedOn") }}
            {{
              new Intl.DateTimeFormat(locale, { dateStyle: "medium" }).format(
                new Date(row.joined_at),
              )
            }}
          </p>
        </div>
      </div>
      <div v-else class="empty-page">
        <div class="empty-icon"><BookOpen :size="32" /></div>
        <h2>{{ t("catalog.myEmpty") }}</h2>
        <p>{{ t("catalog.myEmptySub") }}</p>
        <RouterLink to="/courses" class="button"
          >{{ t("home.explore") }}<ArrowUpRight :size="17"
        /></RouterLink></div
    ></template>
  </div>
</template>
