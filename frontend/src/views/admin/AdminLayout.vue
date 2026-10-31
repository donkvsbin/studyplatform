<script setup lang="ts">
import { useI18n } from "vue-i18n";
const { t } = useI18n();
</script>
<template>
  <div class="container page">
    <div class="admin-header">
      <h1>{{ t("admin.title") }}</h1>
      <RouterLink to="/" class="text-link">{{ t("admin.back") }}</RouterLink>
    </div>
    <nav class="admin-nav">
      <RouterLink to="/admin">{{ t("admin.dashboard") }}</RouterLink
      ><RouterLink to="/admin/courses">{{ t("admin.courses") }}</RouterLink
      ><RouterLink to="/admin/categories">{{
        t("admin.categories")
      }}</RouterLink
      ><RouterLink to="/admin/users">{{ t("admin.users") }}</RouterLink>
    </nav>
    <RouterView />
  </div>
</template>
