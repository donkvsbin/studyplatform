<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import {
  ArrowUpRight,
  ArrowRight,
  Sparkles,
  Check,
  Compass,
  BookOpen,
  Terminal,
  Play,
} from "lucide-vue-next";
import { api } from "../api";
import type { Course, Pagination } from "../types";
import CourseCard from "../components/CourseCard.vue";
import UiError from "../components/UiError.vue";
const { t, locale } = useI18n(),
  courses = ref<Course[]>([]),
  total = ref(0),
  lessonTotal = ref(0),
  busy = ref(true),
  error = ref<unknown>(null);
let sequence = 0;
async function load() {
  const id = ++sequence;
  busy.value = true;
  error.value = null;
  try {
    const result = await api<{ data: Course[]; pagination: Pagination }>(
      "/courses?per_page=24",
    );
    if (id !== sequence) return;
    courses.value = result.data.slice(0, 3);
    total.value = result.pagination.total;
    lessonTotal.value = result.data.reduce((sum, c) => sum + c.lesson_count, 0);
  } catch (e) {
    if (id === sequence) error.value = e;
  } finally {
    if (id === sequence) busy.value = false;
  }
}
watch(locale, load, { immediate: true });
</script>
<template>
  <section class="hero">
    <div class="container hero-grid">
      <div class="hero-copy">
        <span class="hero-badge"><span></span>{{ t("home.badge") }}</span>
        <h1>
          {{ t("home.title1") }}<br /><em>{{ t("home.title2") }}</em>
        </h1>
        <p>{{ t("home.subtitle") }}</p>
        <div class="hero-actions">
          <RouterLink to="/courses" class="button"
            >{{ t("home.explore") }}<ArrowUpRight :size="18" /></RouterLink
          ><RouterLink to="/assistant" class="hero-ai"
            ><Sparkles :size="17" />{{ t("home.ai") }}<ArrowRight :size="15"
          /></RouterLink>
        </div>
        <div class="hero-note">
          <span><Check :size="12" /></span>{{ t("home.note") }}
        </div>
      </div>
      <div class="hero-visual" aria-hidden="true">
        <div class="visual-orbit"></div>
        <div class="floating-tag">
          <Sparkles :size="14" />{{ t("home.codeBadge") }}
        </div>
        <div class="code-window">
          <div class="window-toolbar">
            <span class="window-dots"><i></i><i></i><i></i></span
            ><span>hello-world.js</span><Terminal :size="14" />
          </div>
          <div class="code-content">
            <div class="code-line">
              <span class="line-no">1</span
              ><span class="code-comment">{{ t("home.codeComment") }}</span>
            </div>
            <div class="code-line"><span class="line-no">2</span></div>
            <div class="code-line">
              <span class="line-no">3</span
              ><span><b>const</b> dream = <q>build something</q>;</span>
            </div>
            <div class="code-line">
              <span class="line-no">4</span
              ><span><b>function</b> <strong>start</strong>() {</span>
            </div>
            <div class="code-line">
              <span class="line-no">5</span
              ><span>&nbsp;&nbsp;<b>return</b> <q>one small step</q>;</span>
            </div>
            <div class="code-line">
              <span class="line-no">6</span><span>}</span>
            </div>
            <div class="code-line"><span class="line-no">7</span></div>
            <div class="code-line">
              <span class="line-no">8</span
              ><span><strong>start</strong>();<i class="code-cursor"></i></span>
            </div>
          </div>
          <div class="code-output">
            <span><Terminal :size="14" />OUTPUT</span>
            <p><span>›</span> {{ t("home.codeOutput") }}</p>
          </div>
        </div>
        <div class="preview-note">
          <span class="preview-play"
            ><Play :size="14" fill="currentColor"
          /></span>
          <div>
            <strong>{{ t("home.codeTitle") }}</strong
            ><small>{{ t("home.codeCaption") }}</small>
          </div>
          <span class="preview-check"><Check :size="16" /></span>
        </div>
        <span class="tiny-star">✳</span>
      </div>
    </div>
    <div class="container hero-stats" v-if="!busy && !error">
      <div>
        <strong>{{ total.toString().padStart(2, "0") }}</strong
        ><span>{{ t("home.statCourses") }}</span>
      </div>
      <div>
        <strong>{{ lessonTotal }}</strong
        ><span>{{ t("home.statLessons") }}</span>
      </div>
      <div>
        <strong>02</strong><span>{{ t("home.statLanguage") }}</span>
      </div>
      <div class="stats-note">
        <span class="stats-dot"></span>{{ t("common.free") }} ·
        {{ t("catalog.bilingual") }}
      </div>
    </div>
  </section>
  <section class="container featured-section">
    <div class="section-heading">
      <div>
        <span class="section-kicker">{{ t("home.featuredEyebrow") }}</span>
        <h2>{{ t("home.featured") }}</h2>
        <p>{{ t("home.featuredSub") }}</p>
      </div>
      <RouterLink to="/courses" class="text-link"
        >{{ t("home.allCourses") }}<ArrowUpRight :size="17"
      /></RouterLink>
    </div>
    <UiError :error="error" /><button
      v-if="error"
      class="button button-outline"
      @click="load"
    >
      {{ t("common.retry") }}
    </button>
    <p v-if="busy" role="status" class="loading-state">
      {{ t("common.loading") }}
    </p>
    <div v-else class="course-grid">
      <CourseCard v-for="course in courses" :key="course.id" :course="course" />
    </div>
  </section>
  <section class="path-section">
    <div class="container">
      <span class="section-kicker">{{ t("home.pathEyebrow") }}</span>
      <h2>{{ t("home.pathTitle") }}</h2>
      <div class="path-grid">
        <RouterLink
          v-for="n in 3"
          :key="n"
          :to="n === 3 ? '/assistant' : '/courses'"
          class="path-step"
          ><span class="step-icon"
            ><Compass v-if="n === 1" :size="23" /><BookOpen
              v-else-if="n === 2"
              :size="23" /><Sparkles v-else :size="23" /></span
          ><span class="step-number">0{{ n }}</span>
          <h3>{{ t(`home.path${n}`) }}</h3>
          <p>{{ t(`home.path${n}Sub`) }}</p></RouterLink
        >
      </div>
    </div>
  </section>
  <section class="container">
    <div class="home-cta">
      <div>
        <h2>{{ t("home.cta") }}</h2>
        <p>{{ t("home.ctaSub") }}</p>
      </div>
      <RouterLink to="/courses" class="button"
        >{{ t("home.explore") }}<ArrowUpRight :size="18"
      /></RouterLink>
    </div>
  </section>
</template>
