<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { Check, Monitor, Moon, Sun } from "lucide-vue-next";
import { useTheme } from "../stores/theme";
import type { ThemePreference } from "../utils/theme";

const { t } = useI18n();
const { preference, setPreference } = useTheme();
const open = ref(false),
  root = ref<HTMLElement | null>(null),
  trigger = ref<HTMLButtonElement | null>(null);
const options: ThemePreference[] = ["system", "light", "dark"];
const icon = computed(() =>
  preference.value === "system"
    ? Monitor
    : preference.value === "light"
      ? Sun
      : Moon,
);

async function show() {
  open.value = true;
  await nextTick();
  root.value
    ?.querySelector<HTMLButtonElement>('[aria-checked="true"]')
    ?.focus();
}
function close(returnFocus = false) {
  open.value = false;
  if (returnFocus) trigger.value?.focus();
}
function choose(value: ThemePreference) {
  setPreference(value);
  close(true);
}
function outside(event: PointerEvent) {
  if (!root.value?.contains(event.target as Node)) close();
}
function keydown(event: KeyboardEvent) {
  if (event.key === "Escape") {
    event.preventDefault();
    close(true);
    return;
  }
  const buttons = Array.from(
    root.value?.querySelectorAll<HTMLButtonElement>('[role="menuitemradio"]') ||
      [],
  );
  const index = buttons.indexOf(document.activeElement as HTMLButtonElement);
  let next: number;
  if (event.key === "ArrowDown") next = (index + 1) % buttons.length;
  else if (event.key === "ArrowUp")
    next = (index - 1 + buttons.length) % buttons.length;
  else if (event.key === "Home") next = 0;
  else if (event.key === "End") next = buttons.length - 1;
  else return;
  event.preventDefault();
  buttons[next]?.focus();
}
function focusout(event: FocusEvent) {
  if (!root.value?.contains(event.relatedTarget as Node | null)) close();
}
onMounted(() => document.addEventListener("pointerdown", outside));
onUnmounted(() => document.removeEventListener("pointerdown", outside));
</script>
<template>
  <div ref="root" class="theme-switcher" @focusout="focusout">
    <button
      ref="trigger"
      class="theme-trigger"
      type="button"
      :aria-label="t('theme.choose')"
      :title="`${t('theme.choose')}：${t(`theme.${preference}`)}`"
      aria-haspopup="menu"
      :aria-expanded="open"
      @click="open ? close() : show()"
      @keydown.down.prevent="show"
      @keydown.esc="close(true)"
    >
      <component :is="icon" :size="17" aria-hidden="true" /><span>{{
        t(`theme.${preference}`)
      }}</span>
    </button>
    <div
      v-if="open"
      class="theme-menu"
      role="menu"
      :aria-label="t('theme.choose')"
      @keydown="keydown"
    >
      <button
        v-for="value in options"
        :key="value"
        role="menuitemradio"
        :aria-checked="preference === value"
        type="button"
        @click="choose(value)"
      >
        <Monitor v-if="value === 'system'" :size="16" aria-hidden="true" /><Sun
          v-else-if="value === 'light'"
          :size="16"
          aria-hidden="true"
        /><Moon v-else :size="16" aria-hidden="true" /><span>{{
          t(`theme.${value}`)
        }}</span
        ><Check
          v-if="preference === value"
          :size="15"
          class="theme-check"
          aria-hidden="true"
        />
      </button>
    </div>
  </div>
</template>
