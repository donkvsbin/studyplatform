<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { ArrowLeft } from "lucide-vue-next";
const { t } = useI18n();
</script>
<template>
  <div class="container empty-page">
    <span class="big-number">404</span>
    <h1>{{ t("missing.title") }}</h1>
    <p>{{ t("missing.subtitle") }}</p>
    <RouterLink to="/" class="button"
      ><ArrowLeft :size="18" />{{ t("missing.back") }}</RouterLink
    >
  </div>
</template>
