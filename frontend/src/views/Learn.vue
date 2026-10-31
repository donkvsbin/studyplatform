<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { onBeforeRouteLeave, onBeforeRouteUpdate, useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import { api, json } from "../api";
import type { LearningData, LearningSummary } from "../types";
import MarkdownText from "../components/MarkdownText.vue";
import UiError from "../components/UiError.vue";
import LearningProgress from "../components/LearningProgress.vue";
const route = useRoute(),
  { t, locale } = useI18n();
const data = ref<LearningData | null>(null),
  loading = ref(true),
  saving = ref(false),
  error = ref<unknown>(null),
  saveError = ref<unknown>(null),
  video = ref<HTMLVideoElement | null>(null);
const lessons = computed(
  () => data.value?.course.chapters?.flatMap((c) => c.lessons) || [],
);
const index = computed(() =>
  lessons.value.findIndex((l) => l.id === data.value?.lesson.id),
);
let sequence = 0,
  queue = Promise.resolve(),
  lastSavedAt = 0;
async function save(fields: Record<string, unknown> = {}) {
  const current = data.value;
  if (!current) return;
  const id = current.lesson.id,
    cid = current.course.id;
  queue = queue.then(async () => {
    try {
      const result = await api<{
        data: {
          summary: LearningSummary;
          progress: { completed: boolean; video_position: number };
        };
      }>(`/courses/${cid}/lessons/${id}/progress`, json("PUT", fields));
      if (data.value?.lesson.id === id) {
        data.value.summary = result.data.summary;
        data.value.lesson.progress = result.data.progress;
        saveError.value = null;
      }
    } catch (e) {
      saveError.value = e;
    }
  });
  await queue;
}
function saveVideo() {
  if (video.value && data.value?.lesson.video_url) {
    lastSavedAt = Date.now();
    return save({ video_position: video.value.currentTime });
  }
  return Promise.resolve();
}
function timeupdate() {
  if (video.value && !video.value.paused && Date.now() - lastSavedAt >= 5000)
    void saveVideo();
}
function restore() {
  if (video.value && data.value) {
    video.value.currentTime = Math.min(
      data.value.lesson.progress.video_position,
      Math.max(0, video.value.duration - 0.1),
    );
  }
}
async function load() {
  const id = ++sequence;
  loading.value = true;
  error.value = null;
  try {
    await queue;
    const result = await api<{ data: LearningData }>(
      `/courses/${route.params.courseId}/lessons/${route.params.lessonId}`,
    );
    if (id !== sequence) return;
    data.value = result.data;
    lastSavedAt = Date.now();
    await save({});
  } catch (e) {
    if (id === sequence) error.value = e;
  } finally {
    if (id === sequence) loading.value = false;
  }
}
async function toggle() {
  if (!data.value) return;
  saving.value = true;
  await save({ completed: !data.value.lesson.progress.completed });
  saving.value = false;
}
watch(
  [() => route.params.lessonId, () => route.params.courseId, locale],
  load,
  { immediate: true },
);
onBeforeRouteLeave(async () => {
  await saveVideo();
  await queue;
});
onBeforeRouteUpdate(async () => {
  await saveVideo();
  await queue;
});
</script>
<template>
  <div class="container page">
    <p v-if="loading" role="status">{{ t("common.loading") }}</p>
    <UiError :error="error" /><button
      v-if="error"
      class="button button-outline"
      @click="load"
    >
      {{ t("common.retry") }}
    </button>
    <div v-if="data && !loading && !error" class="study-layout">
      <aside class="study-sidebar panel">
        <RouterLink :to="`/courses/${data.course.id}`" class="text-link"
          >← {{ data.course.title }}</RouterLink
        ><LearningProgress :summary="data.summary" />
        <nav :aria-label="t('catalog.outline')">
          <section v-for="chapter in data.course.chapters" :key="chapter.id">
            <h2>{{ chapter.title }}</h2>
            <RouterLink
              v-for="lesson in chapter.lessons"
              :key="lesson.id"
              :to="`/learn/${data.course.id}/${lesson.id}`"
              :class="{ current: lesson.id === data.lesson.id }"
              ><span>{{
                data.summary.completed_lesson_ids.includes(lesson.id)
                  ? "✓"
                  : "○"
              }}</span
              >{{ lesson.title }}</RouterLink
            >
          </section>
          <RouterLink :to="`/courses/${data.course.id}/quiz`" class="quiz-nav"
            >{{ t("learning.quiz") }} →</RouterLink
          >
        </nav>
      </aside>
      <article class="panel lesson-content">
        <div class="page-heading">
          <div>
            <p class="muted">
              {{ t("learning.title") }} · {{ index + 1 }} / {{ lessons.length }}
            </p>
            <h1>{{ data.lesson.title }}</h1>
          </div>
          <RouterLink
            :to="`/assistant?course=${data.course.id}`"
            class="text-link"
            >{{ t("nav.assistant") }}</RouterLink
          >
        </div>
        <section v-if="data.lesson.video_url" class="lesson-video">
          <video
            ref="video"
            :key="data.lesson.id"
            :src="data.lesson.video_url"
            controls
            preload="metadata"
            playsinline
            @loadedmetadata="restore"
            @timeupdate="timeupdate"
            @pause="saveVideo"
            @ended="saveVideo"
            :aria-label="t('learning.video')"
          ></video>
          <p class="muted small">{{ t("learning.videoHint") }}</p>
        </section>
        <MarkdownText :text="data.lesson.body" /><UiError :error="saveError" />
        <div class="lesson-actions">
          <button class="button" :disabled="saving" @click="toggle">
            {{
              t(
                saving
                  ? "common.pending"
                  : data.lesson.progress.completed
                    ? "learning.unmark"
                    : "learning.mark",
              )
            }}</button
          ><RouterLink
            v-if="lessons[index - 1]"
            class="button button-outline"
            :to="`/learn/${data.course.id}/${lessons[index - 1]!.id}`"
            >{{ t("learning.previous") }}</RouterLink
          ><RouterLink
            v-if="lessons[index + 1]"
            class="button button-outline"
            :to="`/learn/${data.course.id}/${lessons[index + 1]!.id}`"
            @click="saveVideo"
            >{{ t("learning.next") }}</RouterLink
          ><RouterLink
            v-else
            class="button button-outline"
            :to="`/courses/${data.course.id}/quiz`"
            >{{ t("learning.takeQuiz") }}</RouterLink
          >
        </div>
        <p class="muted small">{{ t("learning.completeHint") }}</p>
      </article>
    </div>
  </div>
</template>
