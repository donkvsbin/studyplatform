import { createI18n } from "vue-i18n";
import zh from "./zh-CN";
import en from "./en";
import { zhExtra, enExtra, zhErrors, enErrors } from "./extra";
export type Locale = "zh-CN" | "en";
function initialLocale(): Locale {
  const saved = localStorage.getItem("learnhub-locale");
  return saved === "en" || saved === "zh-CN"
    ? saved
    : navigator.language.startsWith("en")
      ? "en"
      : "zh-CN";
}
export const i18n = createI18n({
  legacy: false,
  locale: initialLocale(),
  fallbackLocale: "zh-CN",
  messages: {
    "zh-CN": { ...zh, ...zhExtra, errors: { ...zh.errors, ...zhErrors } },
    en: { ...en, ...enExtra, errors: { ...en.errors, ...enErrors } },
  },
});
export let explicitlySelected = false;
export function setLocale(value: Locale, explicit = false) {
  if (explicit) explicitlySelected = true;
  i18n.global.locale.value = value;
  localStorage.setItem("learnhub-locale", value);
  document.documentElement.lang = value;
}
