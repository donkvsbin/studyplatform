<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "../api";
import type { Enrollment } from "../types";
import UiError from "../components/UiError.vue";
import LearningProgress from "../components/LearningProgress.vue";
const { t, locale } = useI18n(),
  rows = ref<Enrollment[]>([]),
  loading = ref(true),
  error = ref<unknown>(null);
let sequence = 0;
async function load() {
  const id = ++sequence;
  loading.value = true;
  error.value = null;
  try {
    const result = await api<{ data: Enrollment[] }>("/me/enrollments");
    if (id === sequence) rows.value = result.data;
  } catch (e) {
    if (id === sequence) error.value = e;
  } finally {
    if (id === sequence) loading.value = false;
  }
}
watch(locale, load, { immediate: true });
</script>
<template>
  <div class="container page">
    <div class="page-heading">
      <h1>{{ t("nav.learning") }}</h1>
      <div class="actions">
        <RouterLink to="/results" class="button button-outline">{{
          t("learning.history")
        }}</RouterLink
        ><RouterLink to="/courses" class="button button-outline">{{
          t("nav.courses")
        }}</RouterLink>
      </div>
    </div>
    <UiError :error="error" /><button
      v-if="error"
      class="button button-outline"
      @click="load"
    >
      {{ t("common.retry") }}
    </button>
    <p v-if="loading" role="status">{{ t("common.loading") }}</p>
    <template v-else-if="!error"
      ><div v-if="rows.length" class="course-grid">
        <article
          v-for="row in rows"
          :key="row.id"
          class="panel course-card learning-card"
        >
          <h2>{{ row.course.title }}</h2>
          <template v-if="row.available && row.summary"
            ><LearningProgress :summary="row.summary" />
            <div class="actions">
              <RouterLink
                v-if="row.summary.resume_lesson_id"
                :to="`/learn/${row.course.id}/${row.summary.resume_lesson_id}`"
                class="button"
                >{{
                  t(
                    row.summary.state === "not_started"
                      ? "simple.start"
                      : "simple.continue",
                  )
                }}</RouterLink
              ><RouterLink
                :to="`/courses/${row.course.id}/quiz`"
                class="text-link"
                >{{ t("learning.quiz") }}</RouterLink
              ><RouterLink
                :to="`/courses/${row.course.id}`"
                class="text-link"
                >{{ t("catalog.detail") }}</RouterLink
              >
            </div></template
          >
          <p v-else class="notice">{{ t("catalog.withdrawn") }}</p>
          <p class="muted small">
            {{ t("catalog.joinedOn") }}
            {{
              new Intl.DateTimeFormat(locale, { dateStyle: "medium" }).format(
                new Date(row.joined_at),
              )
            }}
          </p>
        </article>
      </div>
      <div v-else class="empty-page">
        <h2>{{ t("catalog.myEmpty") }}</h2>
        <p>{{ t("catalog.myEmptySub") }}</p>
        <RouterLink to="/courses" class="button">{{
          t("nav.courses")
        }}</RouterLink>
      </div></template
    >
  </div>
</template>
