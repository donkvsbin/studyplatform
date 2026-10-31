<script setup lang="ts">
import { useI18n } from "vue-i18n";
const { t } = useI18n();
</script>
<template>
  <div class="container page empty-page">
    <h1>{{ t("missing.forbidden") }}</h1>
    <RouterLink to="/" class="button">{{ t("missing.back") }}</RouterLink>
  </div>
</template>
