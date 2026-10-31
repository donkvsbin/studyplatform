<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { api, json } from "../api";
import { useAuth } from "../stores/auth";
import type { Course } from "../types";
import UiError from "../components/UiError.vue";
import LearningProgress from "../components/LearningProgress.vue";
const { t, locale } = useI18n(),
  route = useRoute(),
  router = useRouter(),
  auth = useAuth();
const course = ref<Course | null>(null),
  loading = ref(true),
  joining = ref(false),
  error = ref<unknown>(null),
  joinError = ref<unknown>(null),
  success = ref(false);
let sequence = 0;
const startId = computed(
  () =>
    course.value?.summary?.resume_lesson_id ||
    course.value?.chapters?.flatMap((c) => c.lessons)[0]?.id,
);
async function load() {
  const id = ++sequence;
  loading.value = true;
  error.value = null;
  try {
    const result = await api<{ data: Course }>(
      `/courses/${route.params.courseId}`,
    );
    if (id === sequence) course.value = result.data;
  } catch (e) {
    if (id === sequence) error.value = e;
  } finally {
    if (id === sequence) loading.value = false;
  }
}
async function join() {
  if (!auth.user) {
    router.push({ path: "/login", query: { redirect: route.fullPath } });
    return;
  }
  joining.value = true;
  joinError.value = null;
  try {
    await api(`/courses/${course.value!.id}/enrollment`, json("POST"));
    await load();
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
    <RouterLink to="/courses" class="text-link"
      >← {{ t("nav.courses") }}</RouterLink
    >
    <p v-if="loading" role="status">{{ t("common.loading") }}</p>
    <UiError :error="error" /><button
      v-if="error"
      class="button button-outline"
      @click="load"
    >
      {{ t("common.retry") }}</button
    ><template v-if="course && !loading && !error"
      ><section class="panel course-intro">
        <p class="muted">
          {{ course.category.name }} · {{ t(`common.${course.difficulty}`) }} ·
          {{ t("common.free") }}
        </p>
        <h1>{{ course.title }}</h1>
        <p>{{ course.description }}</p>
        <p class="muted small">
          {{ course.chapter_count }} {{ t("common.chapters") }} ·
          {{ course.lesson_count }} {{ t("common.lessons") }} ·
          {{ course.duration_minutes }} {{ t("common.minutes") }}
        </p>
        <LearningProgress
          v-if="course.summary"
          :summary="course.summary"
        /><UiError :error="joinError" />
        <p v-if="success" class="success-box" role="status">
          {{ t("catalog.joinSuccess") }}
        </p>
        <div class="actions">
          <button
            v-if="!course.enrolled"
            class="button"
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
            }}</button
          ><template v-else
            ><RouterLink
              v-if="startId"
              :to="`/learn/${course.id}/${startId}`"
              class="button"
              >{{
                t(
                  course.summary?.state === "not_started"
                    ? "simple.start"
                    : "simple.continue",
                )
              }}</RouterLink
            ><RouterLink
              class="button button-outline"
              :to="`/courses/${course.id}/quiz`"
              >{{ t("learning.quiz") }}</RouterLink
            ><RouterLink to="/my-learning" class="text-link">{{
              t("catalog.joined")
            }}</RouterLink></template
          ><RouterLink
            :to="`/assistant?course=${course.id}`"
            class="text-link"
            >{{ t("catalog.askCourse") }}</RouterLink
          >
        </div>
      </section>
      <section class="section panel">
        <h2>{{ t("catalog.objectives") }}</h2>
        <ul>
          <li v-for="objective in course.objectives" :key="objective">
            {{ objective }}
          </li>
        </ul>
      </section>
      <section class="section">
        <h2>{{ t("catalog.outline") }}</h2>
        <details
          v-for="chapter in course.chapters"
          :key="chapter.id"
          class="chapter-panel panel"
          open
        >
          <summary>{{ chapter.title }}</summary>
          <ul>
            <li v-for="lesson in chapter.lessons" :key="lesson.id">
              <RouterLink
                v-if="course.enrolled"
                :to="`/learn/${course.id}/${lesson.id}`"
                >{{
                  course.summary?.completed_lesson_ids.includes(lesson.id)
                    ? "✓ "
                    : ""
                }}{{ lesson.title }}</RouterLink
              ><span v-else>{{ lesson.title }}</span
              ><small
                >{{ lesson.duration_minutes }} {{ t("common.minutes") }}</small
              >
            </li>
          </ul>
        </details>
      </section></template
    >
  </div>
</template>
