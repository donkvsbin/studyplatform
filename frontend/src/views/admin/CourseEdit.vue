<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import { api, ApiError, json } from "../../api";
import type {
  AdminCourse,
  AdminChapter,
  AdminLesson,
  AdminQuestion,
  AdminQuiz,
} from "../../types/admin";
import UiError from "../../components/UiError.vue";
import LessonEditor from "../../components/admin/LessonEditor.vue";
import QuestionEditor from "../../components/admin/QuestionEditor.vue";
const route = useRoute(),
  { t, locale } = useI18n(),
  id = computed(() => Number(route.params.courseId));
const course = ref<AdminCourse | null>(null),
  quiz = ref<AdminQuiz | null>(null),
  categories = ref<
    { id: number; name_zh: string; name_en: string; archived: boolean }[]
  >([]),
  tab = ref("base"),
  busy = ref(false),
  loading = ref(true),
  saved = ref(false),
  error = ref<unknown>(null);
const form = reactive({
  slug: "",
  title_zh: "",
  title_en: "",
  description_zh: "",
  description_en: "",
  objectivesZh: "",
  objectivesEn: "",
  category_id: 0,
  difficulty: "beginner",
});
const chapterEditor = ref(false),
  chapterId = ref<number | null>(null),
  chapter = reactive({ title_zh: "", title_en: "", sort_order: 0 });
const lessonEditor = ref<{ chapterId: number; lesson?: AdminLesson } | null>(
    null,
  ),
  questionEditor = ref<{ question?: AdminQuestion } | null>(null),
  quizTitles = reactive({ title_zh: "结课测验", title_en: "Course quiz" });
const editable = computed(
  () =>
    !!course.value &&
    !course.value.archived &&
    course.value.status !== "published",
);
async function load(reset = false) {
  loading.value = true;
  try {
    const [c, q, k] = await Promise.all([
      api<{ data: AdminCourse }>(`/admin/courses/${id.value}`),
      api<{ data: AdminQuiz | null }>(`/admin/courses/${id.value}/quiz`),
      api<{ data: typeof categories.value }>("/admin/categories"),
    ]);
    course.value = c.data;
    quiz.value = q.data;
    categories.value = k.data.filter(
      (row) => !row.archived || row.id === c.data.category_id,
    );
    if (reset) {
      const c = course.value;
      Object.assign(form, {
        slug: c.slug,
        title_zh: c.title_zh,
        title_en: c.title_en,
        description_zh: c.description_zh,
        description_en: c.description_en,
        objectivesZh: c.objectives_zh.join("\n"),
        objectivesEn: c.objectives_en.join("\n"),
        category_id: c.category_id,
        difficulty: c.difficulty,
      });
      if (quiz.value)
        Object.assign(quizTitles, {
          title_zh: quiz.value.title_zh,
          title_en: quiz.value.title_en,
        });
    }
  } catch (e) {
    error.value = e;
  } finally {
    loading.value = false;
  }
}
function basePayload() {
  const { objectivesZh, objectivesEn, ...fields } = form;
  return {
    ...fields,
    objectives_zh: objectivesZh
      .split("\n")
      .map((x) => x.trim())
      .filter(Boolean),
    objectives_en: objectivesEn
      .split("\n")
      .map((x) => x.trim())
      .filter(Boolean),
  };
}
async function mutate(task: () => Promise<unknown>) {
  busy.value = true;
  error.value = null;
  saved.value = false;
  try {
    await task();
    await load();
    saved.value = true;
  } catch (e) {
    error.value = e;
  } finally {
    busy.value = false;
  }
}
function saveBase() {
  void mutate(() =>
    api(`/admin/courses/${id.value}`, json("PATCH", basePayload())),
  );
}
async function publish() {
  if (chapterEditor.value || lessonEditor.value || questionEditor.value) {
    error.value = new ApiError("finish_editing");
    return;
  }
  await mutate(async () => {
    await api(`/admin/courses/${id.value}`, json("PATCH", basePayload()));
    await api(`/admin/courses/${id.value}/publish`, json("POST"));
  });
}
function unpublish() {
  void mutate(() => api(`/admin/courses/${id.value}/unpublish`, json("POST")));
}
function openChapter(row?: AdminChapter) {
  chapterId.value = row?.id || null;
  Object.assign(
    chapter,
    row
      ? {
          title_zh: row.title_zh,
          title_en: row.title_en,
          sort_order: row.sort_order,
        }
      : { title_zh: "", title_en: "", sort_order: 0 },
  );
  chapterEditor.value = true;
  saved.value = false;
}
function saveChapter() {
  void mutate(async () => {
    await api(
      `/admin/courses/${id.value}/chapters${chapterId.value ? "/" + chapterId.value : ""}`,
      json(chapterId.value ? "PATCH" : "POST", chapter),
    );
    chapterEditor.value = false;
  });
}
function archive(resource: string, rowId: number) {
  if (window.confirm(t("admin.archiveConfirm")))
    void mutate(() => api(`/admin/${resource}/${rowId}/archive`, json("POST")));
}
function saveQuiz() {
  void mutate(() =>
    api(`/admin/courses/${id.value}/quiz`, json("PUT", quizTitles)),
  );
}
function archiveQuestion(rowId: number) {
  if (window.confirm(t("admin.archiveConfirm")))
    void mutate(() =>
      api(
        `/admin/courses/${id.value}/quiz/questions/${rowId}/archive`,
        json("POST"),
      ),
    );
}
function childSaved() {
  lessonEditor.value = null;
  questionEditor.value = null;
  void load();
  saved.value = true;
}
watch(
  id,
  () => {
    error.value = null;
    void load(true);
  },
  { immediate: true },
);
</script>
<template>
  <RouterLink to="/admin/courses" class="text-link"
    >← {{ t("admin.backCourses") }}</RouterLink
  >
  <p v-if="loading" role="status">{{ t("common.loading") }}</p>
  <UiError :error="error" />
  <p v-if="saved" class="success-box" role="status">{{ t("admin.saved") }}</p>
  <template v-if="course"
    ><div class="page-heading section">
      <div>
        <h2>{{ locale === "en" ? course.title_en : course.title_zh }}</h2>
        <span class="status-chip">{{
          t(
            course.archived
              ? "admin.archived"
              : course.status === "published"
                ? "admin.publishedState"
                : `admin.${course.status}`,
          )
        }}</span>
      </div>
      <div class="actions">
        <button
          v-if="course.status === 'published' && !course.archived"
          class="button button-outline"
          :disabled="busy"
          @click="unpublish"
        >
          {{ t("admin.unpublish") }}</button
        ><button
          v-else-if="!course.archived"
          class="button"
          :disabled="busy"
          @click="publish"
        >
          {{ t("admin.publish") }}</button
        ><RouterLink
          v-if="course.status === 'published' && !course.archived"
          :to="`/courses/${course.id}`"
          class="text-link"
          >{{ t("catalog.detail") }}</RouterLink
        >
      </div>
    </div>
    <p class="notice">
      {{
        t(
          course.archived
            ? "admin.resourceArchived"
            : course.status === "published"
              ? "admin.unpublishHint"
              : "admin.publishHint",
        )
      }}
    </p>
    <div class="editor-tabs">
      <button
        v-for="name in ['base', 'chapters', 'quiz']"
        :key="name"
        :class="{ active: tab === name }"
        @click="tab = name"
      >
        {{ t(`admin.${name}`) }}
      </button>
    </div>
    <section v-show="tab === 'base'" class="panel editor-section">
      <h2>{{ t("admin.base") }}</h2>
      <form @submit.prevent="saveBase">
        <fieldset :disabled="!editable || busy" class="plain-fieldset">
          <div class="form-grid">
            <label
              >{{ t("admin.slug")
              }}<input
                v-model="form.slug"
                required
                maxlength="80"
                pattern="[a-z0-9]+(-[a-z0-9]+)*" /></label
            ><label
              >{{ t("admin.category")
              }}<select v-model.number="form.category_id" required>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ locale === "en" ? cat.name_en : cat.name_zh }}
                </option>
              </select></label
            ><label
              >{{ t("admin.titleZh")
              }}<input
                v-model="form.title_zh"
                required
                maxlength="160" /></label
            ><label
              >{{ t("admin.titleEn")
              }}<input
                v-model="form.title_en"
                required
                maxlength="160" /></label
            ><label
              >{{ t("admin.descriptionZh")
              }}<textarea
                v-model="form.description_zh"
                maxlength="10000"
              ></textarea></label
            ><label
              >{{ t("admin.descriptionEn")
              }}<textarea
                v-model="form.description_en"
                maxlength="10000"
              ></textarea></label
            ><label
              >{{ t("admin.objectivesZh")
              }}<textarea v-model="form.objectivesZh"></textarea></label
            ><label
              >{{ t("admin.objectivesEn")
              }}<textarea v-model="form.objectivesEn"></textarea></label
            ><label
              >{{ t("admin.difficulty")
              }}<select v-model="form.difficulty">
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
          <button class="button section">
            {{ t(busy ? "common.pending" : "admin.save") }}
          </button>
        </fieldset>
      </form>
    </section>
    <section v-show="tab === 'chapters'" class="editor-section">
      <div class="page-heading">
        <h2>{{ t("admin.chapters") }}</h2>
        <button
          class="button"
          :disabled="!editable || busy"
          @click="openChapter()"
        >
          {{ t("admin.addChapter") }}
        </button>
      </div>
      <p v-if="!course.chapters.length" class="muted">
        {{ t("admin.emptyChapters") }}
      </p>
      <section v-if="chapterEditor" class="panel admin-form">
        <h3>{{ t(chapterId ? "admin.edit" : "admin.newChapter") }}</h3>
        <form class="section" @submit.prevent="saveChapter">
          <div class="form-grid">
            <label
              >{{ t("admin.titleZh")
              }}<input
                v-model="chapter.title_zh"
                required
                maxlength="160" /></label
            ><label
              >{{ t("admin.titleEn")
              }}<input
                v-model="chapter.title_en"
                required
                maxlength="160" /></label
            ><label
              >{{ t("admin.sort")
              }}<input
                v-model.number="chapter.sort_order"
                type="number"
                min="0"
                max="10000"
                required
            /></label>
          </div>
          <div class="actions">
            <button class="button" :disabled="busy || !editable">
              {{ t("admin.save") }}</button
            ><button
              type="button"
              class="button button-outline"
              @click="chapterEditor = false"
            >
              {{ t("common.cancel") }}
            </button>
          </div>
        </form>
      </section>
      <section
        v-for="row in course.chapters"
        :key="row.id"
        class="panel admin-chapter section"
      >
        <div class="chapter-heading">
          <h3>
            {{ locale === "en" ? row.title_en : row.title_zh }}
            <span v-if="row.archived" class="muted small">{{
              t("admin.archived")
            }}</span>
          </h3>
          <div v-if="!row.archived" class="actions">
            <button
              class="text-link"
              :disabled="!editable || busy"
              @click="openChapter(row)"
            >
              {{ t("admin.edit") }}</button
            ><button
              class="text-link"
              :disabled="!editable || busy"
              @click="lessonEditor = { chapterId: row.id }"
            >
              {{ t("admin.addLesson") }}</button
            ><button
              class="text-link danger-link"
              :disabled="!editable || busy"
              @click="archive('chapters', row.id)"
            >
              {{ t("admin.archive") }}
            </button>
          </div>
        </div>
        <div v-for="lesson in row.lessons" :key="lesson.id" class="lesson-row">
          <span
            >{{ locale === "en" ? lesson.title_en : lesson.title_zh }}
            <small v-if="lesson.archived">{{
              t("admin.archived")
            }}</small></span
          >
          <div v-if="!lesson.archived && !row.archived" class="actions">
            <button
              class="text-link"
              :disabled="!editable || busy"
              @click="lessonEditor = { chapterId: row.id, lesson }"
            >
              {{ t("admin.edit") }}</button
            ><button
              class="text-link danger-link"
              :disabled="!editable || busy"
              @click="archive('lessons', lesson.id)"
            >
              {{ t("admin.archive") }}
            </button>
          </div>
        </div>
        <LessonEditor
          v-if="lessonEditor?.chapterId === row.id"
          :key="`${row.id}-${lessonEditor.lesson?.id || 'new'}`"
          :course-id="id"
          :chapter-id="row.id"
          :lesson="lessonEditor.lesson"
          @saved="childSaved"
          @cancel="lessonEditor = null"
        />
      </section>
    </section>
    <section v-show="tab === 'quiz'" class="editor-section">
      <h2>{{ t("admin.quiz") }}</h2>
      <form class="panel" @submit.prevent="saveQuiz">
        <fieldset class="plain-fieldset" :disabled="!editable || busy">
          <div class="form-grid">
            <label
              >{{ t("admin.titleZh")
              }}<input
                v-model="quizTitles.title_zh"
                required
                maxlength="160" /></label
            ><label
              >{{ t("admin.titleEn")
              }}<input v-model="quizTitles.title_en" required maxlength="160"
            /></label>
          </div>
          <button class="button section">{{ t("admin.save") }}</button>
        </fieldset>
      </form>
      <p v-if="!quiz" class="notice">{{ t("admin.emptyQuiz") }}</p>
      <template v-else
        ><div class="page-heading section">
          <span class="muted small">{{ t("learning.quizHint") }}</span
          ><button
            class="button"
            :disabled="!editable || busy"
            @click="questionEditor = {}"
          >
            {{ t("admin.addQuestion") }}
          </button>
        </div>
        <article
          v-for="question in quiz.questions"
          :key="question.id"
          class="panel section"
        >
          <div class="chapter-heading">
            <h3>
              {{ locale === "en" ? question.prompt_en : question.prompt_zh }}
              <small v-if="question.archived">{{ t("admin.archived") }}</small>
            </h3>
            <div v-if="!question.archived" class="actions">
              <button
                class="text-link"
                :disabled="!editable || busy"
                @click="questionEditor = { question }"
              >
                {{ t("admin.edit") }}</button
              ><button
                class="text-link danger-link"
                :disabled="!editable || busy"
                @click="archiveQuestion(question.id!)"
              >
                {{ t("admin.archive") }}
              </button>
            </div>
          </div>
        </article>
        <QuestionEditor
          v-if="questionEditor"
          :key="questionEditor.question?.id || 'new'"
          :course-id="id"
          :question="questionEditor.question"
          @saved="childSaved"
          @cancel="questionEditor = null"
      /></template></section
  ></template>
</template>
