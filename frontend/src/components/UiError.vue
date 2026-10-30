<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { AlertCircle } from "lucide-vue-next";
import { ApiError } from "../api";
const props = defineProps<{ error: unknown }>();
const { t, te } = useI18n();
const messages = computed(() => {
  if (!props.error) return [];
  const codes =
    props.error instanceof ApiError
      ? [props.error.code, ...Object.values(props.error.fields || {})]
      : ["server_error"];
  return [...new Set(codes)].map((code) =>
    t(te(`errors.${code}`) ? `errors.${code}` : "errors.server_error"),
  );
});
</script>
<template>
  <div v-if="messages.length" class="error-box" role="alert">
    <AlertCircle :size="18" />
    <div>
      <p v-for="message in messages" :key="message">{{ message }}</p>
    </div>
  </div>
</template>
