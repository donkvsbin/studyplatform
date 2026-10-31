<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "../api";
import type { Attempt, Pagination } from "../types";
import UiError from "../components/UiError.vue";
const { t, locale } = useI18n(),
  rows = ref<Attempt[]>([]),
  selected = ref<Attempt | null>(null),
  page = ref(1),
  pagination = ref<Pagination>({ page: 1, per_page: 20, total: 0, pages: 0 }),
  loading = ref(false),
  error = ref<unknown>(null);
let sequence = 0;
async function load() {
  const id = ++sequence;
  loading.value = true;
  error.value = null;
  try {
    const result = await api<{ data: Attempt[]; pagination: Pagination }>(
      `/me/quiz-attempts?page=${page.value}`,
    );
    if (id !== sequence) return;
    rows.value = result.data;
    pagination.value = result.pagination;
    if (selected.value)
      selected.value = (
        await api<{ data: Attempt }>(`/me/quiz-attempts/${selected.value.id}`)
      ).data;
  } catch (e) {
    if (id === sequence) error.value = e;
  } finally {
    if (id === sequence) loading.value = false;
  }
}
async function show(attempt: Attempt) {
  loading.value = true;
  error.value = null;
  try {
    selected.value = (
      await api<{ data: Attempt }>(`/me/quiz-attempts/${attempt.id}`)
    ).data;
  } catch (e) {
    error.value = e;
  } finally {
    loading.value = false;
  }
}
watch(locale, load);
onMounted(load);
</script>
<template>
  <div class="container page quiz-page">
    <div class="page-heading">
      <h1>{{ t("learning.history") }}</h1>
      <RouterLink to="/my-learning" class="text-link">{{
        t("nav.learning")
      }}</RouterLink>
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
      ><section v-if="selected">
        <button class="text-link" @click="selected = null">
          ← {{ t("common.back") }}
        </button>
        <div class="panel section">
          <h2>{{ selected.course_title }} · {{ t("learning.result") }}</h2>
          <p class="section">
            {{ t("learning.score", { score: selected.score }) }} ·
            {{ t(selected.passed ? "learning.passed" : "learning.failed") }}
          </p>
        </div>
        <article
          v-for="answer in selected.answers"
          :key="answer.question_id"
          class="panel answer-review section"
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
      <template v-else
        ><p v-if="!rows.length" class="notice">{{ t("learning.noHistory") }}</p>
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{{ t("common.course") }}</th>
                <th>{{ t("learning.scoreLabel") }}</th>
                <th>{{ t("admin.status") }}</th>
                <th>{{ t("learning.submittedAt") }}</th>
                <th>{{ t("admin.actions") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="attempt in rows" :key="attempt.id">
                <td>{{ attempt.course_title }}</td>
                <td>{{ attempt.score }}%</td>
                <td>
                  {{
                    t(attempt.passed ? "learning.passed" : "learning.failed")
                  }}
                </td>
                <td>
                  {{
                    new Intl.DateTimeFormat(locale, {
                      dateStyle: "short",
                      timeStyle: "short",
                    }).format(new Date(attempt.submitted_at))
                  }}
                </td>
                <td>
                  <button class="text-link" @click="show(attempt)">
                    {{ t("learning.viewResult") }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <nav v-if="pagination.pages > 1" class="pagination">
          <button
            class="button button-outline"
            :disabled="page <= 1"
            @click="
              page--;
              load();
            "
          >
            {{ t("catalog.prev") }}</button
          ><span>{{
            t("catalog.page", { page, total: pagination.pages })
          }}</span
          ><button
            class="button button-outline"
            :disabled="page >= pagination.pages"
            @click="
              page++;
              load();
            "
          >
            {{ t("catalog.next") }}
          </button>
        </nav></template
      ></template
    >
  </div>
</template>
