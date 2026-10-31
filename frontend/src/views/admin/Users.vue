<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api, json } from "../../api";
import type { Pagination } from "../../types";
import UiError from "../../components/UiError.vue";
interface UserRow {
  id: number;
  nickname: string;
  phone: string;
  role: string;
  is_active: boolean;
}
const { t } = useI18n(),
  rows = ref<UserRow[]>([]),
  query = ref(""),
  page = ref(1),
  pagination = ref<Pagination>({ page: 1, per_page: 20, total: 0, pages: 0 }),
  loading = ref(true),
  busy = ref(false),
  error = ref<unknown>(null);
async function load() {
  loading.value = true;
  error.value = null;
  try {
    const result = await api<{ data: UserRow[]; pagination: Pagination }>(
      `/admin/users?page=${page.value}&q=${encodeURIComponent(query.value)}`,
    );
    rows.value = result.data;
    pagination.value = result.pagination;
  } catch (e) {
    error.value = e;
  } finally {
    loading.value = false;
  }
}
function search() {
  page.value = 1;
  void load();
}
async function toggle(row: UserRow) {
  if (row.is_active && !window.confirm(t("admin.disableConfirm"))) return;
  busy.value = true;
  error.value = null;
  try {
    await api(
      `/admin/users/${row.id}/status`,
      json("PATCH", { is_active: !row.is_active }),
    );
    await load();
  } catch (e) {
    error.value = e;
  } finally {
    busy.value = false;
  }
}
onMounted(load);
</script>
<template>
  <div class="admin-toolbar">
    <h2>{{ t("admin.users") }}</h2>
    <form class="search-form" @submit.prevent="search">
      <input
        v-model="query"
        maxlength="100"
        :aria-label="t('admin.search')"
        :placeholder="t('admin.search')"
      /><button class="button button-small">
        {{ t("catalog.searchButton") }}
      </button>
    </form>
  </div>
  <UiError :error="error" />
  <p v-if="loading" role="status">{{ t("common.loading") }}</p>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>{{ t("admin.nickname") }}</th>
          <th>{{ t("admin.phone") }}</th>
          <th>{{ t("admin.role") }}</th>
          <th>{{ t("admin.status") }}</th>
          <th>{{ t("admin.actions") }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.id">
          <td>{{ row.id }}</td>
          <td>{{ row.nickname }}</td>
          <td>{{ row.phone }}</td>
          <td>
            {{
              t(row.role === "admin" ? "admin.administrator" : "admin.student")
            }}
          </td>
          <td>{{ t(row.is_active ? "admin.enabled" : "admin.disabled") }}</td>
          <td>
            <button
              v-if="row.role !== 'admin'"
              class="text-link"
              :disabled="busy"
              @click="toggle(row)"
            >
              {{ t(row.is_active ? "admin.disable" : "admin.enable") }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="!rows.length && !loading" class="table-empty">
      {{ t("admin.empty") }}
    </p>
  </div>
  <div v-if="pagination.pages > 1" class="pagination">
    <button
      class="button button-outline"
      :disabled="page <= 1"
      @click="
        page--;
        load();
      "
    >
      {{ t("catalog.prev") }}</button
    ><span>{{ t("catalog.page", { page, total: pagination.pages }) }}</span
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
  </div>
</template>
