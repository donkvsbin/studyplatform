<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "../api";
import { useAuth } from "../stores/auth";
import type { Course, Enrollment } from "../types";
import CourseCard from "../components/CourseCard.vue";
import UiError from "../components/UiError.vue";
import {
  ArrowRight,
  BookOpen,
  CheckCheck,
  Code2,
  MessageCircle,
} from "lucide-vue-next";
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
    <section class="home-hero">
      <div class="hero-copy">
        <p class="hero-eyebrow">{{ t("simple.eyebrow") }}</p>
        <h1>{{ t("simple.headline") }}</h1>
        <p class="hero-description">{{ t("simple.intro") }}</p>
        <div class="actions hero-actions">
          <RouterLink class="button" to="/courses"
            >{{ t("simple.start") }}<ArrowRight :size="17" aria-hidden="true"
          /></RouterLink>
          <RouterLink class="button button-outline" to="/my-learning">{{
            t("nav.learning")
          }}</RouterLink>
        </div>
      </div>
      <aside class="learning-guide" :aria-label="t('simple.guide')">
        <div class="guide-heading">
          <BookOpen :size="20" aria-hidden="true" />
          <h2>{{ t("simple.guide") }}</h2>
        </div>
        <p class="muted guide-intro">{{ t("simple.guideHint") }}</p>
        <ol class="guide-steps">
          <li>
            <span class="step-icon"
              ><Code2 :size="18" aria-hidden="true"
            /></span>
            <div>
              <h3>{{ t("simple.stepCourse") }}</h3>
              <p>{{ t("simple.stepCourseHint") }}</p>
            </div>
          </li>
          <li>
            <span class="step-icon"
              ><BookOpen :size="18" aria-hidden="true"
            /></span>
            <div>
              <h3>{{ t("simple.stepLesson") }}</h3>
              <p>{{ t("simple.stepLessonHint") }}</p>
            </div>
          </li>
          <li>
            <span class="step-icon"
              ><CheckCheck :size="18" aria-hidden="true"
            /></span>
            <div>
              <h3>{{ t("simple.stepQuiz") }}</h3>
              <p>{{ t("simple.stepQuizHint") }}</p>
            </div>
          </li>
        </ol>
        <RouterLink class="guide-assistant" to="/assistant"
          ><MessageCircle :size="16" aria-hidden="true" /><span>{{
            t("simple.assistantHint")
          }}</span
          ><ArrowRight :size="16" aria-hidden="true"
        /></RouterLink>
      </aside>
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
        <div>
          <h2>{{ t("simple.recommended") }}</h2>
          <p class="muted small section-description">
            {{ t("simple.coursesHint") }}
          </p>
        </div>
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
