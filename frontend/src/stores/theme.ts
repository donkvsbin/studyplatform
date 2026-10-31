import { computed, ref, watchEffect } from "vue";
import { parseTheme, resolveTheme, type ThemePreference } from "../utils/theme";

const storageKey = "learnhub-theme";
function savedTheme() {
  try {
    return parseTheme(localStorage.getItem(storageKey));
  } catch {
    return "system" as const;
  }
}
const preference = ref<ThemePreference>(savedTheme());
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
  window.addEventListener("storage", (event) => {
    if (event.key === storageKey || event.key === null)
      preference.value = parseTheme(event.newValue);
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
  function setPreference(value: ThemePreference) {
    preference.value = value;
    try {
      localStorage.setItem(storageKey, value);
    } catch {
      /* Keep this session usable without browser storage. */
    }
  }
  return { preference, resolved, setPreference };
}
