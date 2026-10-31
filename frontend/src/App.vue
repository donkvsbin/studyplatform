<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAuth } from "./stores/auth";
import UiError from "./components/UiError.vue";
const { t, locale } = useI18n(),
  auth = useAuth(),
  router = useRouter();
const menu = ref(false),
  error = ref<unknown>(null),
  busy = ref(false);
async function language() {
  try {
    error.value = null;
    await auth.switchLocale(locale.value === "en" ? "zh-CN" : "en");
  } catch (e) {
    error.value = e;
  }
}
async function logout() {
  busy.value = true;
  try {
    await auth.logout();
    await router.push("/");
  } catch (e) {
    error.value = e;
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <a class="skip-link" href="#main">{{ t("nav.skip") }}</a>
  <header class="site-header">
    <div class="container header-inner">
      <RouterLink to="/" class="brand"
        >LearnHub <span v-if="locale !== 'en'">学习坊</span></RouterLink
      ><button
        class="mobile-toggle button button-outline"
        @click="menu = !menu"
        :aria-expanded="menu"
        :aria-label="t('nav.menu')"
      >
        ☰
      </button>
      <nav
        :class="{ open: menu }"
        class="main-nav"
        @click="menu = false"
        aria-label="Main"
      >
        <RouterLink to="/courses">{{ t("nav.courses") }}</RouterLink
        ><RouterLink to="/my-learning">{{ t("nav.learning") }}</RouterLink
        ><RouterLink to="/assistant">{{ t("nav.assistant") }}</RouterLink
        ><RouterLink v-if="auth.user?.role === 'admin'" to="/admin">{{
          t("admin.title")
        }}</RouterLink>
      </nav>
      <div class="nav-actions">
        <button
          class="language-button"
          @click="language"
          :aria-label="locale === 'en' ? '切换为中文' : 'Switch to English'"
        >
          {{ locale === "en" ? "中文" : "EN" }}</button
        ><template v-if="auth.user"
          ><RouterLink
            class="account-link"
            to="/settings"
            :aria-label="t('simple.account')"
            >{{ auth.user.nickname }}</RouterLink
          ><button
            class="text-link"
            @click="logout"
            :disabled="busy"
            :aria-label="t('nav.logout')"
          >
            {{ t("nav.logout") }}
          </button></template
        ><template v-else
          ><RouterLink class="login-link" to="/login">{{
            t("nav.login")
          }}</RouterLink
          ><RouterLink class="button button-small" to="/register">{{
            t("nav.register")
          }}</RouterLink></template
        >
      </div>
    </div>
  </header>
  <div v-if="error" class="container"><UiError :error="error" /></div>
  <main id="main" tabindex="-1"><RouterView /></main>
  <footer class="site-footer">
    <div class="container">{{ t("simple.footer") }}</div>
  </footer>
</template>
