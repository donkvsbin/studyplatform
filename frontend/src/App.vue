<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import {
  Layers3,
  ArrowUpRight,
  Globe2,
  Menu,
  X,
  LogOut,
  Sparkles,
  Settings,
} from "lucide-vue-next";
import { useAuth } from "./stores/auth";
import UiError from "./components/UiError.vue";
const { t, locale } = useI18n(),
  auth = useAuth(),
  router = useRouter();
const logoutBusy = ref(false);
const mobile = ref(false),
  error = ref<unknown>(null);
async function language() {
  try {
    error.value = null;
    await auth.switchLocale(locale.value === "en" ? "zh-CN" : "en");
  } catch (e) {
    error.value = e;
  }
}
async function logout() {
  if (logoutBusy.value) return;
  logoutBusy.value = true;
  try {
    await auth.logout();
    mobile.value = false;
    router.push("/");
  } catch (e) {
    error.value = e;
  } finally {
    logoutBusy.value = false;
  }
}
</script>
<template>
  <a class="skip-link" href="#main">{{ t("nav.skip") }}</a>
  <header class="site-header">
    <div class="nav-wrap">
      <RouterLink to="/" class="brand" aria-label="LearnHub"
        ><span class="brand-icon"><Layers3 :size="23" /></span
        ><span>LearnHub<span class="brand-cn">学习坊</span></span></RouterLink
      >
      <button
        class="icon-button mobile-toggle"
        @click="mobile = !mobile"
        :aria-label="mobile ? t('common.close') : t('nav.menu')"
        :aria-expanded="mobile"
      >
        <X v-if="mobile" /><Menu v-else />
      </button>
      <nav
        :class="['main-nav', { open: mobile }]"
        @click="mobile = false"
        aria-label="Main"
      >
        <RouterLink to="/" exact-active-class="active">{{
          t("nav.home")
        }}</RouterLink
        ><RouterLink to="/courses">{{ t("nav.courses") }}</RouterLink
        ><RouterLink to="/my-learning">{{ t("nav.learning") }}</RouterLink
        ><RouterLink to="/assistant" class="ai-nav"
          ><Sparkles :size="15" />{{ t("nav.assistant") }}</RouterLink
        >
      </nav>
      <div class="nav-actions">
        <button
          class="language-button"
          @click="language"
          :aria-label="locale === 'en' ? '切换为中文' : 'Switch to English'"
        >
          <Globe2 :size="17" /><span>{{
            locale === "en" ? "中文" : "EN"
          }}</span>
        </button>
        <template v-if="auth.user"
          ><RouterLink
            to="/settings"
            class="user-link"
            :title="t('nav.settings')"
            ><span class="avatar">{{ auth.user.nickname.slice(0, 1) }}</span
            ><span class="user-name">{{ auth.user.nickname }}</span
            ><Settings :size="16" /></RouterLink
          ><button
            class="icon-button logout-button"
            :disabled="logoutBusy"
            @click="logout"
            :aria-label="t('nav.logout')"
          >
            <LogOut :size="18" /></button
        ></template>
        <template v-else
          ><RouterLink to="/login" class="login-link">{{
            t("nav.login")
          }}</RouterLink
          ><RouterLink to="/register" class="button button-small"
            >{{ t("nav.register") }}<ArrowUpRight :size="16" /></RouterLink
        ></template>
      </div>
    </div>
  </header>
  <div v-if="error" class="container"><UiError :error="error" /></div>
  <main id="main" tabindex="-1"><RouterView /></main>
  <footer class="site-footer">
    <div class="container footer-wrap">
      <RouterLink to="/" class="brand"
        ><span class="brand-icon"><Layers3 :size="20" /></span
        ><span>LearnHub</span></RouterLink
      >
      <p>{{ t("home.footer") }}</p>
      <span>{{ t("home.footerNote") }}</span>
    </div>
  </footer>
</template>
