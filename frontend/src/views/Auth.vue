<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { api, ApiError, json } from "../api";
import { useAuth } from "../stores/auth";
import { safeRedirect } from "../utils/navigation";
import UiError from "../components/UiError.vue";
const { t, locale } = useI18n(),
  route = useRoute(),
  router = useRouter(),
  auth = useAuth(),
  register = computed(() => route.path === "/register");
const phone = ref(""),
  nickname = ref(""),
  password = ref(""),
  confirm = ref(""),
  busy = ref(false),
  error = ref<unknown>(null);
async function submit() {
  error.value = null;
  if (register.value && password.value !== confirm.value) {
    error.value = new ApiError("password_mismatch");
    return;
  }
  busy.value = true;
  try {
    if (register.value) {
      await api(
        "/auth/register",
        json("POST", {
          phone: phone.value,
          nickname: nickname.value,
          password: password.value,
          confirm_password: confirm.value,
          locale: locale.value,
        }),
      );
      password.value = "";
      confirm.value = "";
      await router.push({
        path: "/login",
        query: { ...route.query, registered: "1" },
      });
    } else {
      await auth.login(phone.value, password.value);
      await router.push(safeRedirect(route.query.redirect));
    }
  } catch (e) {
    error.value = e;
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <div class="container page">
    <section class="panel auth-form">
      <nav class="auth-tabs" :aria-label="t('theme.authArea')">
        <RouterLink
          :to="{ path: '/login', query: { redirect: route.query.redirect } }"
          >{{ t("nav.login") }}</RouterLink
        >
        <RouterLink
          :to="{ path: '/register', query: { redirect: route.query.redirect } }"
          >{{ t("auth.toRegister") }}</RouterLink
        >
      </nav>
      <h1>{{ t(register ? "auth.registerTitle" : "auth.loginTitle") }}</h1>
      <p class="muted">
        {{ t(register ? "auth.registerSubtitle" : "auth.loginSubtitle") }}
      </p>
      <p
        v-if="route.query.registered && !register"
        class="success-box"
        role="status"
      >
        {{ t("auth.registered") }}
      </p>
      <p v-if="route.query.changed" class="success-box" role="status">
        {{ t("auth.passwordChanged") }}
      </p>
      <UiError :error="error" />
      <form @submit.prevent="submit">
        <label v-if="register" for="nickname"
          >{{ t("auth.nickname")
          }}<input
            id="nickname"
            v-model="nickname"
            autocomplete="nickname"
            maxlength="40"
            required /></label
        ><label for="phone"
          >{{ t("auth.phone")
          }}<input
            id="phone"
            v-model="phone"
            type="tel"
            autocomplete="tel"
            maxlength="20"
            required
            aria-describedby="phone-hint" /></label
        ><small id="phone-hint" class="field-hint">{{
          t("auth.phoneHint")
        }}</small
        ><label for="password"
          >{{ t("auth.password")
          }}<input
            id="password"
            v-model="password"
            type="password"
            :autocomplete="register ? 'new-password' : 'current-password'"
            minlength="8"
            maxlength="128"
            required
            :placeholder="t('auth.passwordHint')" /></label
        ><label v-if="register" for="confirm"
          >{{ t("auth.confirm")
          }}<input
            id="confirm"
            v-model="confirm"
            type="password"
            autocomplete="new-password"
            minlength="8"
            maxlength="128"
            required /></label
        ><button class="button" :disabled="busy">
          {{
            t(
              busy
                ? "common.pending"
                : register
                  ? "auth.submitRegister"
                  : "auth.submitLogin",
            )
          }}
        </button>
      </form>
      <p class="muted small">
        {{ t(register ? "auth.privacy" : "auth.forgot") }}
      </p>
    </section>
  </div>
</template>
