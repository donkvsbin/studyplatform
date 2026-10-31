<script setup lang="ts">
import { reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api, json } from "../../api";
import UiError from "../UiError.vue";
import type { AdminQuestion as QuestionRow } from "../../types/admin";
const props = defineProps<{ courseId: number; question?: QuestionRow }>(),
  emit = defineEmits<{ saved: []; cancel: [] }>(),
  { t } = useI18n();
const form = reactive<QuestionRow>(
    props.question
      ? JSON.parse(JSON.stringify(props.question))
      : {
          prompt_zh: "",
          prompt_en: "",
          explanation_zh: "",
          explanation_en: "",
          options: ["a", "b", "c"].map((id) => ({
            id,
            text_zh: "",
            text_en: "",
          })),
          correct_option_id: "a",
          sort_order: 0,
        },
  ),
  busy = ref(false),
  error = ref<unknown>(null);
function add() {
  const id = ["a", "b", "c", "d", "e", "f"].find(
    (id) => !form.options.some((o) => o.id === id),
  );
  if (id) form.options.push({ id, text_zh: "", text_en: "" });
}
function remove(id: string) {
  form.options = form.options.filter((o) => o.id !== id);
  if (form.correct_option_id === id)
    form.correct_option_id = form.options[0]!.id;
}
async function save() {
  busy.value = true;
  error.value = null;
  try {
    const { id, archived, ...fields } = form;
    await api(
      `/admin/courses/${props.courseId}/quiz/questions${id ? "/" + id : ""}`,
      json(id ? "PATCH" : "POST", fields),
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
    <h3>{{ t(question ? "admin.edit" : "admin.addQuestion") }}</h3>
    <UiError :error="error" />
    <form class="section" @submit.prevent="save">
      <div class="form-grid">
        <label
          >{{ t("admin.promptZh")
          }}<textarea
            v-model="form.prompt_zh"
            required
            maxlength="5000"
          ></textarea></label
        ><label
          >{{ t("admin.promptEn")
          }}<textarea
            v-model="form.prompt_en"
            required
            maxlength="5000"
          ></textarea>
        </label>
      </div>
      <fieldset>
        <legend>{{ t("admin.options") }}</legend>
        <div
          v-for="option in form.options"
          :key="option.id"
          class="option-editor"
        >
          <span>{{ option.id.toUpperCase() }}</span
          ><label
            >{{ t("admin.optionZh") }} {{ option.id
            }}<input
              v-model="option.text_zh"
              required
              maxlength="2000" /></label
          ><label
            >{{ t("admin.optionEn") }} {{ option.id
            }}<input
              v-model="option.text_en"
              required
              maxlength="2000" /></label
          ><button
            class="button button-outline button-small"
            type="button"
            @click="remove(option.id)"
            :disabled="form.options.length <= 2"
          >
            {{ t("admin.removeOption") }}
          </button>
        </div>
        <button
          class="text-link section"
          type="button"
          @click="add"
          :disabled="form.options.length >= 6"
        >
          {{ t("admin.addOption") }}
        </button>
      </fieldset>
      <div class="form-grid">
        <label
          >{{ t("admin.correct")
          }}<select v-model="form.correct_option_id">
            <option
              v-for="option in form.options"
              :key="option.id"
              :value="option.id"
            >
              {{ option.id.toUpperCase() }}
            </option>
          </select></label
        ><label
          >{{ t("admin.sort")
          }}<input
            v-model.number="form.sort_order"
            type="number"
            min="0"
            max="10000"
            required /></label
        ><label
          >{{ t("admin.explanationZh")
          }}<textarea
            v-model="form.explanation_zh"
            maxlength="10000"
          ></textarea></label
        ><label
          >{{ t("admin.explanationEn")
          }}<textarea
            v-model="form.explanation_en"
            maxlength="10000"
          ></textarea>
        </label>
      </div>
      <div class="actions">
        <button class="button" :disabled="busy">
          {{ t(busy ? "common.pending" : "admin.save") }}</button
        ><button
          class="button button-outline"
          type="button"
          @click="emit('cancel')"
          :disabled="busy"
        >
          {{ t("common.cancel") }}
        </button>
      </div>
    </form>
  </section>
</template>
