<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { api, json } from "../../api";
import UiError from "../../components/UiError.vue";
interface CourseRow {
  id: number;
  title_zh: string;
  title_en: string;
  status: string;
  archived: boolean;
}
interface CategoryRow {
  id: number;
  name_zh: string;
  name_en: string;
  archived: boolean;
}
const { t, locale } = useI18n(),
  router = useRouter(),
  rows = ref<CourseRow[]>([]),
  categories = ref<CategoryRow[]>([]),
  editor = ref(false),
  busy = ref(false),
  loading = ref(true),
  error = ref<unknown>(null);
const form = reactive({
  slug: "",
  title_zh: "",
  title_en: "",
  category_id: 0,
  difficulty: "beginner",
});
async function load() {
  loading.value = true;
  error.value = null;
  try {
    const [c, k] = await Promise.all([
      api<{ data: CourseRow[] }>("/admin/courses"),
      api<{ data: CategoryRow[] }>("/admin/categories"),
    ]);
    rows.value = c.data;
    categories.value = k.data.filter((row) => !row.archived);
    if (!form.category_id) form.category_id = categories.value[0]?.id || 0;
  } catch (e) {
    error.value = e;
  } finally {
    loading.value = false;
  }
}
async function create() {
  busy.value = true;
  error.value = null;
  try {
    const result = await api<{ data: CourseRow }>(
      "/admin/courses",
      json("POST", form),
    );
    await router.push(`/admin/courses/${result.data.id}/edit`);
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
    await api(`/admin/courses/${id}/archive`, json("POST"));
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
    <h2>{{ t("admin.courses") }}</h2>
    <button class="button" @click="editor = !editor" :disabled="busy">
      {{ t("admin.newCourse") }}
    </button>
  </div>
  <UiError :error="error" />
  <p v-if="loading" role="status">{{ t("common.loading") }}</p>
  <section v-if="editor" class="panel">
    <h2>{{ t("admin.newCourse") }}</h2>
    <p v-if="!categories.length" class="notice">
      {{ t("admin.noCategories") }}
    </p>
    <form class="section" @submit.prevent="create">
      <div class="form-grid">
        <label
          >{{ t("admin.slug")
          }}<input
            v-model="form.slug"
            required
            pattern="[a-z0-9]+(-[a-z0-9]+)*"
            maxlength="80" /></label
        ><label
          >{{ t("admin.category")
          }}<select v-model.number="form.category_id" required>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ locale === "en" ? cat.name_en : cat.name_zh }}
            </option>
          </select></label
        ><label
          >{{ t("admin.titleZh")
          }}<input v-model="form.title_zh" required maxlength="160" /></label
        ><label
          >{{ t("admin.titleEn")
          }}<input v-model="form.title_en" required maxlength="160"
        /></label>
      </div>
      <div class="actions">
        <button class="button" :disabled="busy || !categories.length">
          {{ t(busy ? "common.pending" : "admin.save") }}</button
        ><button
          class="button button-outline"
          type="button"
          @click="editor = false"
        >
          {{ t("common.cancel") }}
        </button>
      </div>
    </form>
  </section>
  <div class="table-wrap section">
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>{{ t("common.course") }}</th>
          <th>{{ t("admin.status") }}</th>
          <th>{{ t("admin.actions") }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.id">
          <td>{{ row.id }}</td>
          <td>{{ locale === "en" ? row.title_en : row.title_zh }}</td>
          <td>
            <span class="status-chip">{{
              t(
                row.archived
                  ? "admin.archived"
                  : row.status === "published"
                    ? "admin.publishedState"
                    : `admin.${row.status}`,
              )
            }}</span>
          </td>
          <td>
            <div class="actions">
              <RouterLink
                class="text-link"
                :to="`/admin/courses/${row.id}/edit`"
                >{{ t("admin.edit") }}</RouterLink
              ><button
                v-if="!row.archived"
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
</template>
