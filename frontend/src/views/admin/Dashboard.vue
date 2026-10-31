<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "../../api";
import UiError from "../../components/UiError.vue";
const { t } = useI18n(),
  stats = ref<Record<string, number> | null>(null),
  error = ref<unknown>(null),
  loading = ref(true);
async function load() {
  loading.value = true;
  error.value = null;
  try {
    stats.value = (
      await api<{ data: Record<string, number> }>("/admin/stats")
    ).data;
  } catch (e) {
    error.value = e;
  } finally {
    loading.value = false;
  }
}
onMounted(load);
const labels: Record<string, string> = {
  users: "totalUsers",
  published_courses: "published",
  enrollments: "enrollments",
  completed_courses: "completed",
};
</script>
<template>
  <h2 class="subheading">{{ t("admin.dashboard") }}</h2>
  <p v-if="loading" role="status">{{ t("common.loading") }}</p>
  <UiError :error="error" /><button
    v-if="error"
    class="button button-outline"
    @click="load"
  >
    {{ t("common.retry") }}
  </button>
  <div v-if="stats" class="stats-grid">
    <article v-for="(label, key) in labels" :key="key" class="panel">
      <span>{{ t(`admin.${label}`) }}</span
      ><strong>{{ stats[key] }}</strong>
    </article>
  </div>
  <div class="actions section">
    <RouterLink class="button" to="/admin/courses">{{
      t("admin.courses")
    }}</RouterLink
    ><RouterLink class="button button-outline" to="/admin/categories">{{
      t("admin.categories")
    }}</RouterLink
    ><RouterLink class="button button-outline" to="/admin/users">{{
      t("admin.users")
    }}</RouterLink>
  </div>
</template>
