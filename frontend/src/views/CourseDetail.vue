<script setup lang="ts">
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import {
  ArrowLeft,
  ArrowUpRight,
  BookOpen,
  Clock3,
  Globe2,
  Check,
  ChevronDown,
  FileText,
  Sparkles,
} from "lucide-vue-next";
import { api, json } from "../api";
import { useAuth } from "../stores/auth";
import type { Course } from "../types";
import CourseCover from "../components/CourseCover.vue";
import UiError from "../components/UiError.vue";
const { t, locale } = useI18n(),
  route = useRoute(),
  router = useRouter(),
  auth = useAuth();
const course = ref<Course | null>(null),
  busy = ref(true),
  joining = ref(false),
  error = ref<unknown>(null),
  joinError = ref<unknown>(null),
  success = ref(false);
let sequence = 0;
async function load() {
  const id = ++sequence;
  busy.value = true;
  error.value = null;
  try {
    const result = await api<{ data: Course }>(
      `/courses/${route.params.courseId}`,
    );
    if (id === sequence) course.value = result.data;
  } catch (e) {
    if (id === sequence) error.value = e;
  } finally {
    if (id === sequence) busy.value = false;
  }
}
async function join() {
  if (!auth.user) {
    router.push({ path: "/login", query: { redirect: route.fullPath } });
    return;
  }
  if (!course.value) return;
  joining.value = true;
  joinError.value = null;
  try {
    await api(`/courses/${course.value.id}/enrollment`, json("POST"));
    course.value.enrolled = true;
    success.value = true;
  } catch (e) {
    joinError.value = e;
  } finally {
    joining.value = false;
  }
}
watch([() => route.params.courseId, locale], load, { immediate: true });
</script>
<template>
  <div class="container page detail-page">
    <RouterLink to="/courses" class="text-link back-link"
      ><ArrowLeft :size="16" />{{ t("nav.courses") }}</RouterLink
    >
    <p v-if="busy" class="loading-state" role="status">
      {{ t("common.loading") }}
    </p>
    <UiError :error="error" /><button
      v-if="error"
      class="button button-outline"
      @click="load"
    >
      {{ t("common.retry") }}</button
    ><template v-if="course && !busy && !error"
      ><div class="detail-layout">
        <div class="detail-main">
          <div class="detail-tags">
            <span class="pill">{{ course.category.name }}</span
            ><span>{{ t(`common.${course.difficulty}`) }}</span
            ><span>{{ t("common.free") }}</span>
          </div>
          <h1>{{ course.title }}</h1>
          <p class="detail-description">{{ course.description }}</p>
          <div class="detail-meta">
            <span
              ><BookOpen :size="17" />{{ course.lesson_count }}
              {{ t("common.lessons") }}</span
            ><span
              ><Clock3 :size="17" />{{ course.duration_minutes }}
              {{ t("common.minutes") }}</span
            ><span><Globe2 :size="17" />{{ t("catalog.bilingual") }}</span>
          </div>
          <section class="objectives-panel">
            <h2>{{ t("catalog.objectives") }}</h2>
            <ul>
              <li v-for="objective in course.objectives" :key="objective">
                <Check :size="17" />{{ objective }}
              </li>
            </ul>
          </section>
          <section class="outline-section">
            <div class="outline-heading">
              <h2>{{ t("catalog.outline") }}</h2>
              <span
                >{{ course.chapter_count }} {{ t("common.chapters") }} ·
                {{ course.lesson_count }} {{ t("common.lessons") }}</span
              >
            </div>
            <details
              v-for="(chapter, index) in course.chapters"
              :key="chapter.id"
              class="chapter-panel"
              open
            >
              <summary>
                <span class="chapter-index">{{
                  String(index + 1).padStart(2, "0")
                }}</span
                ><strong>{{ chapter.title }}</strong
                ><ChevronDown :size="17" />
              </summary>
              <ul>
                <li v-for="lesson in chapter.lessons" :key="lesson.id">
                  <FileText :size="16" /><span>{{ lesson.title }}</span
                  ><small
                    >{{ lesson.duration_minutes }}
                    {{ t("common.minutes") }}</small
                  >
                </li>
              </ul>
            </details>
            <p class="outline-note">{{ t("catalog.noBody") }}</p>
          </section>
        </div>
        <aside class="detail-sidebar">
          <CourseCover :kind="course.cover_kind" large />
          <div class="join-panel">
            <span class="section-kicker">{{ t("catalog.yourStart") }}</span>
            <div class="price">
              {{ t("common.free") }}<span>{{ t("common.beginner") }}</span>
            </div>
            <UiError :error="joinError" />
            <p v-if="success" class="success-box" role="status">
              {{ t("catalog.joinSuccess") }}
            </p>
            <button
              v-if="!course.enrolled"
              class="button wide"
              :disabled="joining"
              @click="join"
            >
              {{
                t(
                  joining
                    ? "common.pending"
                    : auth.user
                      ? "catalog.join"
                      : "catalog.loginJoin",
                )
              }}<ArrowUpRight :size="18" /></button
            ><RouterLink v-else to="/my-learning" class="button wide"
              ><Check :size="18" />{{ t("catalog.joined") }}</RouterLink
            >
            <p class="join-note">
              {{
                t(course.enrolled ? "catalog.joinedNote" : "catalog.joinNote")
              }}
            </p>
            <hr />
            <p class="included-title">{{ t("catalog.included") }}</p>
            <ul>
              <li>
                <BookOpen :size="16" />{{ course.lesson_count }}
                {{ t("common.lessons") }}
              </li>
              <li>
                <Clock3 :size="16" />{{ course.duration_minutes }}
                {{ t("common.minutes") }}
              </li>
              <li><Globe2 :size="16" />{{ t("catalog.bilingual") }}</li>
            </ul>
            <RouterLink
              :to="`/assistant?course=${course.id}`"
              class="ask-course"
              ><Sparkles :size="16" />{{ t("catalog.askCourse")
              }}<ArrowUpRight :size="15"
            /></RouterLink>
          </div>
        </aside></div
    ></template>
  </div>
</template>
