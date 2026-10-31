<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAuth } from "./stores/auth";
import UiError from "./components/UiError.vue";
import ThemeSwitcher from "./components/ThemeSwitcher.vue";
import { BookOpen, LogOut, Menu, X } from "lucide-vue-next";
const { t, locale } = useI18n(),
  auth = useAuth(),
  router = useRouter(),
  route = useRoute();
const menu = ref(false),
  error = ref<unknown>(null),
  busy = ref(false);
const languageBusy = ref(false);
async function language() {
  if (languageBusy.value) return;
  languageBusy.value = true;
  try {
    error.value = null;
    await auth.switchLocale(locale.value === "en" ? "zh-CN" : "en");
  } catch (e) {
    error.value = e;
  } finally {
    languageBusy.value = false;
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
      <RouterLink to="/" class="brand" aria-label="LearnHub"
        ><span class="brand-symbol"
          ><BookOpen :size="18" aria-hidden="true" /></span
        ><span class="brand-name"
          >LearnHub<small v-if="locale !== 'en'">学习坊</small></span
        ></RouterLink
      ><button
        class="mobile-toggle button button-outline"
        @click="menu = !menu"
        :aria-expanded="menu"
        :aria-label="menu ? t('common.close') : t('nav.menu')"
      >
        <X v-if="menu" :size="19" aria-hidden="true" /><Menu
          v-else
          :size="19"
          aria-hidden="true"
        />
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
        <ThemeSwitcher />
        <button
          class="language-button"
          :disabled="languageBusy || busy"
          :aria-busy="languageBusy"
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
            class="text-link logout-button"
            @click="logout"
            :disabled="busy || languageBusy"
            :aria-label="t('nav.logout')"
          >
            <LogOut :size="16" aria-hidden="true" /><span>{{
              t("nav.logout")
            }}</span>
          </button></template
        ><template v-else
          ><RouterLink
            class="login-link button button-small"
            :to="{
              path: '/login',
              query:
                route.path === '/'
                  ? {}
                  : {
                      redirect:
                        route.query.redirect ||
                        (['/login', '/register'].includes(route.path)
                          ? undefined
                          : route.fullPath),
                    },
            }"
            >{{ t("nav.login") }}</RouterLink
          ></template
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
