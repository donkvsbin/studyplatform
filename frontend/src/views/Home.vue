<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "../api";
import { useAuth } from "../stores/auth";
import type { Course, Enrollment } from "../types";
import CourseCard from "../components/CourseCard.vue";
import UiError from "../components/UiError.vue";
const { t, locale } = useI18n(),
  auth = useAuth(),
  courses = ref<Course[]>([]),
  recent = ref<Enrollment[]>([]),
  loading = ref(true),
  error = ref<unknown>(null);
let sequence = 0;
async function load() {
  const id = ++sequence;
  loading.value = true;
  error.value = null;
  try {
    const [c, e] = await Promise.all([
      api<{ data: Course[] }>("/courses?per_page=3"),
      auth.user
        ? api<{ data: Enrollment[] }>("/me/enrollments")
        : Promise.resolve({ data: [] as Enrollment[] }),
    ]);
    if (id === sequence) {
      courses.value = c.data;
      recent.value = e.data.filter((x) => x.available).slice(0, 2);
    }
  } catch (e) {
    if (id === sequence) error.value = e;
  } finally {
    if (id === sequence) loading.value = false;
  }
}
watch([locale, () => auth.user?.id], load, { immediate: true });
</script>
<template>
  <div class="container page home-page">
    <section class="welcome-panel">
      <h1>{{ t("simple.home") }}</h1>
      <p>{{ t("simple.intro") }}</p>
      <div class="actions">
        <RouterLink class="button" to="/courses">{{
          t("nav.courses")
        }}</RouterLink
        ><RouterLink class="button button-outline" to="/my-learning">{{
          t("nav.learning")
        }}</RouterLink
        ><RouterLink class="text-link" to="/assistant"
          >{{ t("nav.assistant") }} →</RouterLink
        >
      </div>
    </section>
    <UiError :error="error" /><button
      v-if="error"
      class="button button-outline"
      @click="load"
    >
      {{ t("common.retry") }}
    </button>
    <p v-if="loading" role="status">{{ t("common.loading") }}</p>
    <section v-if="recent.length" class="section">
      <h2>{{ t("simple.recent") }}</h2>
      <div class="continue-list">
        <RouterLink
          v-for="row in recent"
          :key="row.id"
          :to="
            row.summary?.resume_lesson_id
              ? `/learn/${row.course.id}/${row.summary.resume_lesson_id}`
              : `/courses/${row.course.id}`
          "
          class="panel continue-row"
          ><strong>{{ row.course.title }}</strong
          ><span
            >{{ row.summary?.percent }}% · {{ t("simple.continue") }} →</span
          ></RouterLink
        >
      </div>
    </section>
    <section class="section">
      <div class="page-heading">
        <h2>{{ t("simple.recommended") }}</h2>
        <RouterLink to="/courses" class="text-link"
          >{{ t("simple.viewCourses") }} →</RouterLink
        >
      </div>
      <div class="course-grid">
        <CourseCard
          v-for="course in courses"
          :key="course.id"
          :course="course"
        />
      </div>
    </section>
  </div>
</template>
