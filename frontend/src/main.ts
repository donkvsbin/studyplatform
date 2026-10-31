import { createApp } from "vue";
import App from "./App.vue";
import { createPinia } from "pinia";
import { i18n, setLocale } from "./locales";
import { router } from "./router";
import { useAuth } from "./stores/auth";
import { resetCsrf } from "./api";
import { initTheme } from "./stores/theme";
import "./styles/main.css";

initTheme();
setLocale(i18n.global.locale.value as "en" | "zh-CN");
const pinia = createPinia();
window.addEventListener("learnhub:session-expired", () => {
  useAuth(pinia).user = null;
  resetCsrf();
  const current = router.currentRoute.value;
  if (current.meta.auth || current.path === "/assistant") {
    void router.replace({
      path: "/login",
      query: { redirect: current.fullPath },
    });
  }
});
createApp(App).use(pinia).use(i18n).use(router).mount("#app");
