<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api, json } from "../../api";
import UiError from "../../components/UiError.vue";
interface CategoryRow {
  id: number;
  slug: string;
  name_zh: string;
  name_en: string;
  sort_order: number;
  archived: boolean;
}
const { t, locale } = useI18n(),
  rows = ref<CategoryRow[]>([]),
  error = ref<unknown>(null),
  busy = ref(false),
  loading = ref(true),
  editor = ref(false),
  editId = ref<number | null>(null),
  saved = ref(false);
const form = reactive({ slug: "", name_zh: "", name_en: "", sort_order: 0 });
async function load() {
  loading.value = true;
  error.value = null;
  try {
    rows.value = (await api<{ data: CategoryRow[] }>("/admin/categories")).data;
  } catch (e) {
    error.value = e;
  } finally {
    loading.value = false;
  }
}
function edit(row?: CategoryRow) {
  editId.value = row?.id || null;
  Object.assign(
    form,
    row
      ? {
          slug: row.slug,
          name_zh: row.name_zh,
          name_en: row.name_en,
          sort_order: row.sort_order,
        }
      : { slug: "", name_zh: "", name_en: "", sort_order: 0 },
  );
  editor.value = true;
  saved.value = false;
}
async function save() {
  busy.value = true;
  error.value = null;
  try {
    await api(
      `/admin/categories${editId.value ? "/" + editId.value : ""}`,
      json(editId.value ? "PATCH" : "POST", form),
    );
    editor.value = false;
    await load();
    saved.value = true;
  } catch (e) {
    error.value = e;
  } finally {
    busy.value = false;
  }
}
async function archive(id: number) {
  if (!window.confirm(t("admin.archiveConfirm"))) return;
  busy.value = true;
  error.value = null;
  try {
    await api(`/admin/categories/${id}/archive`, json("POST"));
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
    <h2>{{ t("admin.categories") }}</h2>
    <button class="button" @click="edit()" :disabled="busy">
      {{ t("admin.newCategory") }}
    </button>
  </div>
  <UiError :error="error" />
  <p v-if="saved" class="success-box" role="status">{{ t("admin.saved") }}</p>
  <p v-if="loading" role="status">{{ t("common.loading") }}</p>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>{{ t("admin.nameZh") }}</th>
          <th>{{ t("admin.nameEn") }}</th>
          <th>{{ t("admin.sort") }}</th>
          <th>{{ t("admin.status") }}</th>
          <th>{{ t("admin.actions") }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.id">
          <td>{{ row.id }}</td>
          <td>{{ row.name_zh }}</td>
          <td>{{ row.name_en }}</td>
          <td>{{ row.sort_order }}</td>
          <td>{{ t(row.archived ? "admin.archived" : "admin.active") }}</td>
          <td>
            <div v-if="!row.archived" class="actions">
              <button class="text-link" @click="edit(row)" :disabled="busy">
                {{ t("admin.edit") }}</button
              ><button
                class="text-link danger-link"
                @click="archive(row.id)"
                :disabled="busy"
              >
                {{ t("admin.archive") }}
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="!rows.length && !loading" class="table-empty">
      {{ t("admin.empty") }}
    </p>
  </div>
  <section v-if="editor" class="panel admin-form">
    <h2>{{ t(editId ? "admin.edit" : "admin.newCategory") }}</h2>
    <form class="section" @submit.prevent="save">
      <div class="form-grid">
        <label
          >{{ t("admin.slug")
          }}<input
            v-model="form.slug"
            required
            maxlength="80"
            pattern="[a-z0-9]+(-[a-z0-9]+)*" /></label
        ><label
          >{{ t("admin.sort")
          }}<input
            v-model.number="form.sort_order"
            type="number"
            min="0"
            max="10000"
            required /></label
        ><label
          >{{ t("admin.nameZh")
          }}<input v-model="form.name_zh" required maxlength="80" /></label
        ><label
          >{{ t("admin.nameEn")
          }}<input v-model="form.name_en" required maxlength="80"
        /></label>
      </div>
      <div class="actions">
        <button class="button" :disabled="busy">
          {{ t(busy ? "common.pending" : "admin.save") }}</button
        ><button
          type="button"
          class="button button-outline"
          @click="editor = false"
          :disabled="busy"
        >
          {{ t("common.cancel") }}
        </button>
      </div>
    </form>
  </section>
</template>
