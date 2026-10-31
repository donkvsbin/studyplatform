<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { Moon, Sun } from "lucide-vue-next";
import { useTheme } from "../stores/theme";

const { t } = useI18n();
const { resolved, toggleTheme } = useTheme();
const action = computed(() =>
  t(resolved.value === "dark" ? "theme.toLight" : "theme.toDark"),
);
</script>
<template>
  <button
    class="theme-trigger"
    type="button"
    :aria-label="action"
    :title="action"
    @click="toggleTheme"
  >
    <Moon v-if="resolved === 'dark'" :size="17" aria-hidden="true" />
    <Sun v-else :size="17" aria-hidden="true" />
  </button>
</template>
