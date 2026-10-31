<script setup lang="ts">
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import { api, json, ApiError } from "../api";
import type { QuizData, Attempt, Pagination } from "../types";
import UiError from "../components/UiError.vue";
const route = useRoute(),
  { t, locale } = useI18n();
const quiz = ref<QuizData | null>(null),
  answers = ref<Record<string, string>>({}),
  result = ref<Attempt | null>(null),
  history = ref<Attempt[]>([]),
  loading = ref(true),
  busy = ref(false),
  error = ref<unknown>(null);
const historyPage = ref(1),
  historyPagination = ref<Pagination>({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0,
  }),
  stale = ref(false);
let sequence = 0,
  lastFingerprint = "",
  submissionId = "";
async function load() {
  const id = ++sequence;
  loading.value = true;
  error.value = null;
  try {
    const [q, h] = await Promise.all([
      api<{ data: QuizData }>(`/courses/${route.params.courseId}/quiz`),
      api<{ data: Attempt[]; pagination: Pagination }>(
        `/me/quiz-attempts?course_id=${route.params.courseId}&page=${historyPage.value}`,
      ),
    ]);
    if (id !== sequence) return;
    if (
      quiz.value &&
      quiz.value.version !== q.data.version &&
      Object.keys(answers.value).length
    ) {
      stale.value = true;
      error.value = new ApiError("quiz_changed");
    } else quiz.value = q.data;
    history.value = h.data;
    historyPagination.value = h.pagination;
    if (result.value)
      result.value = (
        await api<{ data: Attempt }>(`/me/quiz-attempts/${result.value.id}`)
      ).data;
  } catch (e) {
    if (id === sequence) error.value = e;
  } finally {
    if (id === sequence) loading.value = false;
  }
}
async function submit() {
  if (!quiz.value || stale.value) return;
  error.value = null;
  if (quiz.value.questions.some((q) => !answers.value[q.id])) {
    error.value = new ApiError("invalid_answers");
    return;
  }
  busy.value = true;
  const fingerprint = JSON.stringify({
    version: quiz.value.version,
    answers: answers.value,
  });
  if (fingerprint !== lastFingerprint) {
    lastFingerprint = fingerprint;
    submissionId = crypto.randomUUID();
  }
  try {
    result.value = (
      await api<{ data: Attempt }>(
        `/courses/${route.params.courseId}/quiz/attempts`,
        json("POST", {
          submission_id: submissionId,
          version: quiz.value.version,
          answers: answers.value,
        }),
      )
    ).data;
    historyPage.value = 1;
    await load();
  } catch (e) {
    error.value = e;
  } finally {
    busy.value = false;
  }
}
function retake() {
  result.value = null;
  answers.value = {};
  lastFingerprint = "";
  error.value = null;
}
function reload() {
  retake();
  stale.value = false;
  quiz.value = null;
  void load();
}
function historyTo(value: number) {
  historyPage.value = value;
  void load();
}
async function show(attempt: Attempt) {
  busy.value = true;
  error.value = null;
  try {
    result.value = (
      await api<{ data: Attempt }>(`/me/quiz-attempts/${attempt.id}`)
    ).data;
  } catch (e) {
    error.value = e;
  } finally {
    busy.value = false;
  }
}
watch([() => route.params.courseId, locale], load, { immediate: true });
</script>
<template>
  <div class="container page quiz-page">
    <RouterLink :to="`/courses/${route.params.courseId}`" class="text-link"
      >← {{ t("catalog.detail") }}</RouterLink
    >
    <p v-if="loading" role="status">{{ t("common.loading") }}</p>
    <UiError :error="error" /><button
      v-if="error"
      class="button button-outline"
      @click="reload"
    >
      {{ t("learning.refreshQuiz") }}</button
    ><template v-if="quiz && !loading"
      ><div class="page-heading">
        <div>
          <h1>{{ quiz.title }}</h1>
          <p class="muted">{{ t("learning.quizHint") }}</p>
        </div>
        <RouterLink
          v-if="quiz.summary.resume_lesson_id"
          :to="`/learn/${quiz.course_id}/${quiz.summary.resume_lesson_id}`"
          class="button button-outline"
          >{{ t("learning.backStudy") }}</RouterLink
        >
      </div>
      <p v-if="quiz.summary.best_score !== null" class="notice">
        {{ t("learning.latest", { score: quiz.summary.latest_score }) }} ·
        {{ t("learning.best", { score: quiz.summary.best_score }) }}
      </p>
      <form v-if="!result" @submit.prevent="submit">
        <fieldset
          v-for="(question, index) in quiz.questions"
          :key="question.id"
          class="panel quiz-question"
        >
          <legend>{{ t("learning.question", { number: index + 1 }) }}</legend>
          <h2>{{ question.prompt }}</h2>
          <label
            v-for="option in question.options"
            :key="option.id"
            class="radio-option"
            ><input
              v-model="answers[String(question.id)]"
              type="radio"
              :name="`question-${question.id}`"
              :value="option.id"
              required
            />{{ option.text }}</label
          >
        </fieldset>
        <button class="button" :disabled="busy || stale">
          {{ t(busy ? "common.pending" : "learning.submit") }}
        </button>
      </form>
      <section v-else class="quiz-result">
        <div class="panel result-summary" role="status">
          <h2>
            {{ t(result.passed ? "learning.passed" : "learning.failed") }}
          </h2>
          <p>
            {{ t("learning.score", { score: result.score }) }} ·
            {{ result.correct_count }} / {{ result.total_count }}
          </p>
          <p>{{ t(`learning.${quiz.summary.state}`) }}</p>
          <button class="button" :disabled="busy" @click="retake">
            {{ t("learning.retake") }}
          </button>
        </div>
        <article
          v-for="answer in result.answers"
          :key="answer.question_id"
          class="panel answer-review"
        >
          <h3>{{ answer.is_correct ? "✓" : "×" }} {{ answer.prompt }}</h3>
          <p>
            {{ t("learning.selected") }}：{{
              answer.options.find((o) => o.id === answer.selected_option_id)
                ?.text
            }}
          </p>
          <p>
            {{ t("learning.correct") }}：{{
              answer.options.find((o) => o.id === answer.correct_option_id)
                ?.text
            }}
          </p>
          <p class="muted">
            {{ t("learning.explanation") }}：{{ answer.explanation }}
          </p>
        </article>
      </section>
      <section class="history-section">
        <h2>{{ t("learning.history") }}</h2>
        <p v-if="!history.length" class="muted">
          {{ t("learning.noHistory") }}
        </p>
        <ul v-else class="history-list">
          <li v-for="attempt in history" :key="attempt.id">
            <span>{{
              new Intl.DateTimeFormat(locale, {
                dateStyle: "short",
                timeStyle: "short",
              }).format(new Date(attempt.submitted_at))
            }}</span
            ><strong>{{ attempt.score }}%</strong
            ><span>{{
              t(attempt.passed ? "learning.passed" : "learning.failed")
            }}</span
            ><button
              class="text-link"
              type="button"
              :disabled="busy"
              @click="show(attempt)"
            >
              {{ t("learning.viewResult") }}
            </button>
          </li>
        </ul>
        <nav v-if="historyPagination.pages > 1" class="pagination">
          <button
            class="button button-outline"
            :disabled="historyPage <= 1 || busy"
            @click="historyTo(historyPage - 1)"
          >
            {{ t("catalog.prev") }}</button
          ><span>{{
            t("catalog.page", {
              page: historyPage,
              total: historyPagination.pages,
            })
          }}</span
          ><button
            class="button button-outline"
            :disabled="historyPage >= historyPagination.pages || busy"
            @click="historyTo(historyPage + 1)"
          >
            {{ t("catalog.next") }}
          </button>
        </nav>
      </section></template
    >
  </div>
</template>
