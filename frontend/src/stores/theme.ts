import { computed, ref, watchEffect } from "vue";
import { resolveTheme, type ThemePreference } from "../utils/theme";

// A manual choice lasts only for this document. Every new visit starts with
// the system appearance, including browsers with an older saved preference.
const preference = ref<ThemePreference>("system");
const media = window.matchMedia("(prefers-color-scheme: dark)");
const systemDark = ref(media.matches);
const resolved = computed(() =>
  resolveTheme(preference.value, systemDark.value),
);
let initialized = false;

export function initTheme() {
  if (initialized) return;
  initialized = true;
  media.addEventListener("change", (event) => {
    systemDark.value = event.matches;
  });
  watchEffect(() => {
    const root = document.documentElement;
    root.dataset.theme = resolved.value;
    root.dataset.themePreference = preference.value;
    root.style.colorScheme = resolved.value;
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute(
        "content",
        resolved.value === "dark" ? "#0c0c0c" : "#fafafa",
      );
  });
}

export function useTheme() {
  function toggleTheme() {
    preference.value = resolved.value === "dark" ? "light" : "dark";
  }
  return { resolved, toggleTheme };
}
