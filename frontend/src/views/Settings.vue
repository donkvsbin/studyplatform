<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { UserRound, ShieldCheck } from "lucide-vue-next";
import { useAuth, type User } from "../stores/auth";
import { api, json, resetCsrf } from "../api";
import { setLocale, type Locale } from "../locales";
import UiError from "../components/UiError.vue";
const { t } = useI18n(),
  auth = useAuth(),
  router = useRouter();
const nickname = ref(auth.user?.nickname || ""),
  preferred = ref<Locale>(auth.user?.locale || "zh-CN");
const old = ref(""),
  next = ref(""),
  confirm = ref(""),
  busy = ref(""),
  saved = ref(false),
  profileError = ref<unknown>(null),
  passwordError = ref<unknown>(null);
watch(
  () => auth.user?.locale,
  (value) => {
    if (value) preferred.value = value;
  },
);
async function save() {
  busy.value = "profile";
  profileError.value = null;
  saved.value = false;
  try {
    auth.user = (
      await api<{ data: User }>(
        "/me",
        json("PATCH", { nickname: nickname.value, locale: preferred.value }),
      )
    ).data;
    setLocale(preferred.value, true);
    saved.value = true;
  } catch (e) {
    profileError.value = e;
  } finally {
    busy.value = "";
  }
}
async function password() {
  busy.value = "password";
  passwordError.value = null;
  try {
    await api(
      "/me/password",
      json("POST", {
        old_password: old.value,
        new_password: next.value,
        confirm_password: confirm.value,
      }),
    );
    auth.user = null;
    resetCsrf();
    router.push("/login?changed=1");
  } catch (e) {
    passwordError.value = e;
  } finally {
    busy.value = "";
  }
}
</script>
<template>
  <div class="container page settings-page">
    <span class="section-kicker">YOUR SPACE</span>
    <h1>{{ t("auth.settingsTitle") }}</h1>
    <p class="page-subtitle">{{ t("auth.settingsSub") }}</p>
    <div class="settings-grid">
      <section class="panel">
        <h2><UserRound :size="21" />{{ t("auth.profile") }}</h2>
        <UiError :error="profileError" />
        <p v-if="saved" class="success-box" role="status">
          {{ t("common.saved") }}
        </p>
        <form @submit.prevent="save">
          <label for="setting-phone"
            >{{ t("auth.phone")
            }}<input
              id="setting-phone"
              :value="auth.user?.phone"
              disabled /></label
          ><small class="field-hint">{{ t("auth.phoneFixed") }}</small
          ><label for="setting-name"
            >{{ t("auth.nickname")
            }}<input
              id="setting-name"
              v-model="nickname"
              required
              maxlength="40" /></label
          ><label for="setting-locale"
            >{{ t("auth.locale")
            }}<select id="setting-locale" v-model="preferred">
              <option value="zh-CN">简体中文</option>
              <option value="en">English</option>
            </select></label
          ><button class="button" :disabled="!!busy">
            {{ t(busy === "profile" ? "common.pending" : "common.save") }}
          </button>
        </form>
      </section>
      <section class="panel">
        <h2><ShieldCheck :size="21" />{{ t("auth.security") }}</h2>
        <UiError :error="passwordError" />
        <form @submit.prevent="password">
          <label for="old-password"
            >{{ t("auth.oldPassword")
            }}<input
              id="old-password"
              v-model="old"
              type="password"
              autocomplete="current-password"
              required
              minlength="8"
              maxlength="128" /></label
          ><label for="new-password"
            >{{ t("auth.newPassword")
            }}<input
              id="new-password"
              v-model="next"
              type="password"
              autocomplete="new-password"
              required
              minlength="8"
              maxlength="128" /></label
          ><label for="new-confirm"
            >{{ t("auth.confirm")
            }}<input
              id="new-confirm"
              v-model="confirm"
              type="password"
              autocomplete="new-password"
              required
              minlength="8"
              maxlength="128" /></label
          ><button class="button button-outline" :disabled="!!busy">
            {{
              t(busy === "password" ? "common.pending" : "auth.changePassword")
            }}
          </button>
        </form>
      </section>
    </div>
  </div>
</template>
