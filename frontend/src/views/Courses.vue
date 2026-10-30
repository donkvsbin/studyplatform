<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { Search, ArrowLeft, ArrowRight, BookOpen } from "lucide-vue-next";
import { api } from "../api";
import type { Course, Category, Pagination } from "../types";
import CourseCard from "../components/CourseCard.vue";
import UiError from "../components/UiError.vue";
const { t, locale } = useI18n(),
  route = useRoute(),
  router = useRouter();
const categories = ref<Category[]>([]),
  courses = ref<Course[]>([]),
  search = ref(""),
  busy = ref(true),
  error = ref<unknown>(null),
  pagination = ref<Pagination>({ page: 1, per_page: 6, total: 0, pages: 0 });
const category = computed(() => String(route.query.category || "")),
  difficulty = computed(() => String(route.query.difficulty || ""));
let sequence = 0;
async function load() {
  const id = ++sequence;
  busy.value = true;
  error.value = null;
  search.value = String(route.query.q || "");
  const query = new URLSearchParams();
  for (const key of ["category", "difficulty", "q", "page"])
    if (route.query[key]) query.set(key, String(route.query[key]));
  query.set("per_page", "6");
  try {
    const [cats, result] = await Promise.all([
      api<{ data: Category[] }>("/categories"),
      api<{ data: Course[]; pagination: Pagination }>(`/courses?${query}`),
    ]);
    if (id !== sequence) return;
    categories.value = cats.data;
    courses.value = result.data;
    pagination.value = result.pagination;
  } catch (e) {
    if (id === sequence) error.value = e;
  } finally {
    if (id === sequence) busy.value = false;
  }
}
function filter(key: string, value: string) {
  router.push({
    path: "/courses",
    query: { ...route.query, [key]: value || undefined, page: undefined },
  });
}
function page(value: number) {
  router.push({ query: { ...route.query, page: String(value) } });
}
watch([() => route.fullPath, locale], load, { immediate: true });
</script>
<template>
  <section class="catalog-hero">
    <div class="container">
      <span class="section-kicker">{{ t("catalog.eyebrow") }}</span>
      <h1>{{ t("catalog.title") }}</h1>
      <p>{{ t("catalog.subtitle") }}</p>
      <form class="search-form" @submit.prevent="filter('q', search)">
        <Search :size="19" /><input
          v-model="search"
          type="search"
          :aria-label="t('catalog.searchLabel')"
          :placeholder="t('catalog.search')"
          maxlength="100"
        /><button class="button button-small">
          {{ t("catalog.searchButton") }}
        </button>
      </form>
    </div>
  </section>
  <div class="container catalog-content">
    <div class="catalog-filters">
      <div class="category-tabs" :aria-label="t('catalog.category')">
        <button
          :class="{ selected: !category }"
          @click="filter('category', '')"
        >
          {{ t("common.all") }}</button
        ><button
          v-for="cat in categories"
          :key="cat.id"
          :class="{ selected: category === String(cat.id) }"
          @click="filter('category', String(cat.id))"
        >
          {{ cat.name }}
        </button>
      </div>
      <label class="difficulty-filter"
        >{{ t("catalog.difficulty")
        }}<select
          :value="difficulty"
          @change="
            filter('difficulty', ($event.target as HTMLSelectElement).value)
          "
        >
          <option value="">{{ t("common.all") }}</option>
          <option
            v-for="level in ['beginner', 'intermediate', 'advanced']"
            :key="level"
            :value="level"
          >
            {{ t(`common.${level}`) }}
          </option>
        </select></label
      >
    </div>
    <div class="results-heading">
      <span>{{ t("catalog.count", { count: pagination.total }) }}</span
      ><button
        v-if="Object.keys(route.query).length"
        class="text-link clear-button"
        @click="router.push('/courses')"
      >
        {{ t("catalog.clear") }}
      </button>
    </div>
    <UiError :error="error" /><button
      v-if="error"
      class="button button-outline"
      @click="load"
    >
      {{ t("common.retry") }}
    </button>
    <p v-if="busy" class="loading-state" role="status">
      {{ t("common.loading") }}
    </p>
    <template v-else-if="!error"
      ><div v-if="courses.length" class="course-grid">
        <CourseCard
          v-for="course in courses"
          :key="course.id"
          :course="course"
        />
      </div>
      <div v-else class="empty-page catalog-empty">
        <div class="empty-icon"><BookOpen :size="30" /></div>
        <h2>{{ t("catalog.empty") }}</h2>
        <p>{{ t("catalog.emptySub") }}</p>
        <button class="button button-outline" @click="router.push('/courses')">
          {{ t("catalog.clear") }}
        </button>
      </div>
      <nav
        v-if="pagination.pages > 1"
        class="pagination"
        :aria-label="
          t('catalog.page', { page: pagination.page, total: pagination.pages })
        "
      >
        <button
          class="button button-outline button-small"
          :disabled="pagination.page <= 1"
          @click="page(pagination.page - 1)"
        >
          <ArrowLeft :size="15" />{{ t("catalog.prev") }}</button
        ><span>{{
          t("catalog.page", { page: pagination.page, total: pagination.pages })
        }}</span
        ><button
          class="button button-outline button-small"
          :disabled="pagination.page >= pagination.pages"
          @click="page(pagination.page + 1)"
        >
          {{ t("catalog.next") }}<ArrowRight :size="15" />
        </button></nav
    ></template>
  </div>
</template>
