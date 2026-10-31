<script setup lang="ts">
import { reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api, json } from "../../api";
import UiError from "../UiError.vue";
import MarkdownText from "../MarkdownText.vue";
interface LessonRow {
  id?: number;
  title_zh: string;
  title_en: string;
  body_zh: string;
  body_en: string;
  video_url: string | null;
  duration_minutes: number;
  sort_order: number;
  archived?: boolean;
}
const props = defineProps<{
    courseId: number;
    chapterId: number;
    lesson?: LessonRow;
  }>(),
  emit = defineEmits<{ saved: []; cancel: [] }>(),
  { t, locale } = useI18n();
const form = reactive<LessonRow>(
    props.lesson
      ? { ...props.lesson }
      : {
          title_zh: "",
          title_en: "",
          body_zh: "",
          body_en: "",
          video_url: null,
          duration_minutes: 15,
          sort_order: 0,
        },
  ),
  busy = ref(false),
  error = ref<unknown>(null),
  preview = ref(false);
async function save() {
  busy.value = true;
  error.value = null;
  try {
    const { id, archived, ...fields } = form;
    await api(
      `/admin/courses/${props.courseId}/chapters/${props.chapterId}/lessons${id ? "/" + id : ""}`,
      json(id ? "PATCH" : "POST", {
        ...fields,
        video_url: fields.video_url || null,
      }),
    );
    emit("saved");
  } catch (e) {
    error.value = e;
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <section class="inline-editor">
    <h3>{{ t(lesson ? "admin.edit" : "admin.newLesson") }}</h3>
    <UiError :error="error" />
    <form class="section" @submit.prevent="save">
      <div class="form-grid">
        <label
          >{{ t("admin.titleZh")
          }}<input v-model="form.title_zh" required maxlength="160" /></label
        ><label
          >{{ t("admin.titleEn")
          }}<input v-model="form.title_en" required maxlength="160" /></label
        ><label
          >{{ t("admin.duration")
          }}<input
            v-model.number="form.duration_minutes"
            type="number"
            min="1"
            max="10000"
            required /></label
        ><label
          >{{ t("admin.sort")
          }}<input
            v-model.number="form.sort_order"
            type="number"
            min="0"
            max="10000"
            required /></label
        ><label class="span-2"
          >{{ t("admin.video")
          }}<input
            v-model="form.video_url"
            maxlength="500"
            placeholder="/demo/web-welcome.mp4" /></label
        ><label class="span-2"
          >{{ t("admin.bodyZh")
          }}<textarea
            v-model="form.body_zh"
            rows="8"
            maxlength="50000"
          ></textarea></label
        ><label class="span-2"
          >{{ t("admin.bodyEn")
          }}<textarea
            v-model="form.body_en"
            rows="8"
            maxlength="50000"
          ></textarea>
        </label>
      </div>
      <button type="button" class="text-link" @click="preview = !preview">
        {{ t("admin.preview") }}
      </button>
      <div v-if="preview" class="editor-preview">
        <MarkdownText :text="locale === 'en' ? form.body_en : form.body_zh" />
      </div>
      <div class="actions">
        <button class="button" :disabled="busy">
          {{ t(busy ? "common.pending" : "admin.save") }}</button
        ><button
          type="button"
          class="button button-outline"
          @click="emit('cancel')"
          :disabled="busy"
        >
          {{ t("common.cancel") }}
        </button>
      </div>
    </form>
  </section>
</template>
